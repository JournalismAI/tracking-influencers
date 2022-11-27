let options = {};
const path = require('path');

if (process.env.NODE_ENV !== 'production') {
    require('dotenv-yaml').config({
        path: path.join(__dirname, '../env.yaml')
    });

    options = {
        keyFilename: process.env.KEYFILENAME,
        projectId: process.env.PROJECT_ID
    };
}

const fsp = require('fs').promises;
const fetch = require('node-fetch');
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

async function uploadCF(pathToFile, options) {

    const signedUploadUrl = (await client.generateUploadUrl({
        parent: `projects/${options.project}/locations/${options.region}`
    }))[0].uploadUrl;

    const zipBuf = await fsp.readFile(pathToFile);

    await fetch(signedUploadUrl, {
        method: 'PUT',
        headers: {
            'content-type': 'application/zip',
            'x-goog-content-length-range': '0,104857600',
        },
        body: zipBuf,
    });

    console.log('uploaded zip to google signed url')

    return signedUploadUrl;
}

async function updateCF(signedUploadUrl, options) {

    const updateOptions = {
        function: {
            name: `projects/${options.project}/locations/${options.region}/functions/${options.name}`,
            httpsTrigger: {
                url: `https://${options.region}-${options.project}.cloudfunctions.net/${options.name}`,
            },
            entryPoint: options.entrypoint || options.name,
            runtime: options.runtime,
            sourceUploadUrl: signedUploadUrl,
            availableMemoryMb: 256,
            timeout: {
                seconds: 120
            }
        },
        updateMask: null
    };

    await client.updateFunction(updateOptions);
    console.log(`updated function ${options.name}`);
}

async function createCF(signedUploadUrl, options) {

    const name = `projects/${options.project}/locations/${options.region}/functions/${options.name}`;

    const createOptions = {
        location: `projects/${options.project}/locations/${options.region}`,
        function: {
            name,
            httpsTrigger: {
                url: `https://${options.region}-${options.project}.cloudfunctions.net/${options.name}`
            },
            entryPoint: options.entrypoint || options.name,
            runtime: options.runtime,
            sourceUploadUrl: signedUploadUrl,
            availableMemoryMb: 256,
            timeout: {
                seconds: 120
            }
        }
    };

    await client.createFunction(createOptions);
    console.log(`created function ${name}`);
}

async function deploy(pathToZip, options) {

    const res = await outcome(client.getFunction({
        name: `projects/${options.project}/locations/${options.region}/functions/${options.name}`
    }));

    const signedUploadUrl = await uploadCF(pathToZip, {
        project: options.project,
        region: options.region,
    });

    if (res.success) {

        const [cf] = res.result;
        console.log(`updating: ${cf.name}`);

        return await updateCF(signedUploadUrl, {
            name: options.name,
            project: options.project,
            region: options.region,
            runtime: options.runtime,
            entryPoint: options.entryPoint
        });
    }

    await createCF(signedUploadUrl, {
        ...options
    });

    return `https://${options.region}-${options.project}.cloudfunctions.net/${options.name}`;
}

async function init(data) {
    const current = data.shift();
    await deploy(current.zip, current.options);
    if (data.length) {
        return init(data);
    }
}

function generate(name, data, core, zip) {
    return data.map((item, index) => {
        const options = {
            ...core
        };
        options.region = item;
        options.name = `${name}-${index + 1}`;
        return {
            options,
            zip
        };
    })
}

(async () => {

    const pullzip = path.join(__dirname, '../source/proxy-pull.zip');
    const imagezip = path.join(__dirname, '../source/image-proxy.zip');

    const pullregions = (process.env.PULL_CF_REGIONS) ? process.env.PULL_CF_REGIONS.split(',').map(item => item.trim()) : [];
    const imageregions = (process.env.PULL_IMAGE_REGIONS) ? process.env.PULL_IMAGE_REGIONS.split(',').map(item => item.trim()) : [];

    let core = {
        name: '',
        project: process.env.PROJECT_ID,
        region: '',
        runtime: 'nodejs16',
        entrypoint: 'incomming'
    };

    if (!pullregions.length) {
        console.log('Missing regions for pull cf');
    } else {
        await init(generate(process.env.PULL_CF, pullregions, core, pullzip));
    }

    if (!imageregions.length) {
        console.log('Missing regions for image cf');
    } else {
        await init(generate(process.env.PULL_IMAGE, imageregions, core, imagezip));
    }

})();