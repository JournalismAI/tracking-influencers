let options = {};

if (process.env.NODE_ENV !== 'production') {

    options = {
        keyFilename: process.env.KEYFILENAME,
        projectId: process.env.PROJECT_ID
    };
}

const useragents = require('./useragents');
const GoogleAuth = require('google-auth-library').GoogleAuth;
const CloudFunctionsServiceClient = require('@google-cloud/functions').CloudFunctionsServiceClient;

const auth = new GoogleAuth(options);
const client = new CloudFunctionsServiceClient(options);

const shutdown = [];
let cfProxies = 0;

function timeout(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function pick(object, keys) {
    const filteredEntries = Object.entries(object).filter(([key, _value]) => keys.includes(key));
    return Object.fromEntries(filteredEntries);
}

const outcome = (promise) => {
    return promise
        .then(result => ({
            success: true,
            result
        }))
        .catch(error => ({
            success: false,
            error
        }));
};

async function getCF() {

    const [functions] = await client.listFunctions({
        parent: `projects/${process.env.PROJECT_ID}/locations/-`,
    });

    const list = functions.map(item => pick(item, ['name', 'httpsTrigger'])).filter(item => item.name.includes(process.env.PULL_CF));

    if (!list.length) {
        console.log('No pull proxy found');
    }

    return list.map(item => item.httpsTrigger.url);
}

const getFunction = (async () => {

    const proxies = await getCF();

    cfProxies = proxies.length;

    const proxy = proxies.map(url => {
        return {
            url,
            targetAudience: url
        };
    });

    let entries = proxy.entries();

    return () => {
        let item = entries.next();
        if (!item.done) {
            return item.value[1];
        }
        entries = proxy.entries();
        return entries.next().value[1];
    };

})();

async function request(payload) {

    const item = (await getFunction)();

    if (shutdown.includes(item.url)) {
        if (shutdown.length === cfProxies) {
            console.log('No more proxies available');
            return process.exit();
        }
        return request(payload);
    }

    const client = await auth.getIdTokenClient(item.targetAudience);

    payload.headers['user-agent'] = (await useragents.init)();

    const res = await outcome(client.request({
        url: item.url,
        method: 'POST',
        data: {
            payload
        }
    }));

    if (res.success) {
        return res.result.data;
    }

    console.log('Pull ' + item.url + ' - ' + res.error.code + ' - ' + res.error.response.data.message);

    if (res.error.response.data.message.includes('feedback_required')) {
        shutdown.push(item.url);
        return request(payload);
    }

    if (res.error.response.data.message.includes('Please wait a few minutes') || res.error.response.data.message.includes('checkpoint_required')) {
        shutdown.push(item.url);
        return request(payload);
    }

    if (Number(res.error.code) === 500) {
        await timeout(10000);
        return request(payload);
    }

    if (Number(res.error.code) === 404) {
        return {
            data: {
                user: null
            },
            status: 'ok'
        }
    }

    return request(payload);
}

module.exports = {
    request
};