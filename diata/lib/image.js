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

function pick(object, keys) {
    const filteredEntries = Object.entries(object).filter(([key, _value]) => keys.includes(key));
    return Object.fromEntries(filteredEntries);
}

async function getCF() {

    const [functions] = await client.listFunctions({
        parent: `projects/${process.env.PROJECT_ID}/locations/-`,
    });

    const list = functions.map(item => pick(item, ['name', 'httpsTrigger'])).filter(item => item.name.includes(process.env.PULL_IMAGE));

    if (!list.length) {
        console.log('No image proxy found');
    }

    return list.map(item => item.httpsTrigger.url);
}

const getFunction = (async () => {

    const proxies = await getCF();

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

    console.log('Image: ' + res.error.code + ' - ' + res.error.response.data.message);

    if (res.error.response.data.message.includes('Please wait a few minutes')) {
        await timeout(60000);
    }

    if (res.error.code === 500) {
        console.dir(res);
        await timeout(10000);
    }

    return request(payload);
}

module.exports = {
    request
};