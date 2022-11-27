let options = {};

if (process.env.NODE_ENV !== 'production') {
    require('dotenv-yaml').config({
        path: require('path').join(__dirname, '../env.yaml')
    });

    options = {
        keyFilename: process.env.KEYFILENAME,
        projectId: process.env.PROJECT_ID
    };
}

const CloudFunctionsServiceClient = require('@google-cloud/functions').CloudFunctionsServiceClient;
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

async function cleanup(data, status = []) {
    const name = data.shift();

    const del = await outcome(client.deleteFunction({
        name
    }));

    if (del.success) {
        status.push(name);
    }

    if (data.length) {
        return cleanup(data, status);
    }

    return status;

}

(async () => {

    const [functions] = await client.listFunctions({
        parent: `projects/${process.env.PROJECT_ID}/locations/-`,
    });

    const pull = functions.map(item => pick(item, ['name'])).filter(item => item.name.includes(process.env.PULL_CF));
    const image = functions.map(item => pick(item, ['name'])).filter(item => item.name.includes(process.env.PULL_IMAGE));

    const list = [...pull, ...image].map(item => item.name);

    if (list.length) {
        const done = await cleanup(list);
        console.log('Deleted:\n' + done.join('\n'));
    }

})();