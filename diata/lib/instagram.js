const fs = require('fs').promises;
const constants = require('fs').constants;
const path = require('path');
const url = require('url');
const randomInt = require('random-int');
const percent = require('percent-value');
const mkdirp = require('mkdirp');
const dayjs = require('dayjs');
const prettyHrtime = require('pretty-hrtime');
const pull = require('./pull');
const download = require('./download');
const auth = require('./auth');
const kml = require('./kml');

function timeout(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
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

function extractSidecar(core, base) {
    return core.map(edge => {

        const content = {
            ...base
        };

        const imageUrl = edge.image_versions2.candidates.slice(0, 1).shift();

        content.id = edge.id;
        content.parentId = base.id;
        content.width = edge.original_width;
        content.height = edge.original_height;
        content.imageUrl = imageUrl.url;
        content.file = path.basename(url.parse(imageUrl.url).pathname);
        content.isVideo = edge.video_duration ? true : false;
        content.accessibility_caption = edge.accessibility_caption;
        content.commerciality_status = edge.commerciality_status;
        content.tagged = (edge.usertags && edge.usertags.in.length) ? edge.usertags.in.map(item => {
            const {
                profile_pic_url,
                ...rest
            } = item.user;
            rest.url = `https://${process.env.INSTAGRAM_HOST}/${rest.username}`
            return rest;
        }) : [];

        return content;
    });
}

async function extractPostDetails(data, output) {

    const content = data.map(edge => {
        let hasCaption = edge.caption ? edge.caption : null;

        const imageUrl = (edge.carousel_media) ? edge.carousel_media.shift().image_versions2.candidates.slice(0, 1).shift() : edge.image_versions2.candidates.slice(0, 1).shift();

        const base = {
            id: edge.id,
            ownerId: edge.user.pk,
            parentId: null,
            ownerUsername: edge.user.username,
            shortCode: edge.code,
            url: `https://${process.env.INSTAGRAM_HOST}/p/${edge.code}/`,
            width: edge.original_width,
            height: edge.original_height,
            imageUrl: imageUrl.url,
            file: path.basename(url.parse(imageUrl.url).pathname),
            isVideo: edge.video_duration ? true : false,
            accessibility_caption: edge.accessibility_caption,
            caption: hasCaption ? hasCaption.text : '',
            commentsCount: edge.comment_count,
            commentsDisabled: !edge.comment_likes_enabled,
            timestamp: edge.taken_at,
            date: dayjs(edge.taken_at * 1000).format('YYYY-MM-DDTHH:mm:ss'),
            likesCount: edge.like_count,
            lat: edge.lat || null,
            lng: edge.lng || null,
            locationId: (edge.location) ? edge.location.pk : null,
            locationPublicPage: false,
            locationName: (edge.location) ? edge.location.name : null,
            locationSlug: (edge.location) ? edge.location.short_name : null,
            location: (edge.location) ? `https://${process.env.INSTAGRAM_HOST}/explore/locations/${edge.location.pk}/${edge.location.facebook_places_id}/` : null,
            product_type: edge.product_type || null,
            is_paid_partnership: edge.is_paid_partnership,
            commerciality_status: edge.commerciality_status,
            should_request_ads: edge.should_request_ads,
            tagged: (edge.usertags && edge.usertags.in.length) ? edge.usertags.in.map(item => {
                const {
                    profile_pic_url,
                    ...rest
                } = item.user;
                rest.url = `https://${process.env.INSTAGRAM_HOST}/${rest.username}`
                return rest;
            }) : []
        };

        base.children = (edge.carousel_media && edge.carousel_media.length) ? extractSidecar(edge.carousel_media, base) : []

        return base;
    });

    const list = content.reduce((out, item) => {
        const {
            children,
            tagged,
            ...rest
        } = item;
        const sidecar = item.children.map(main => {
            const {
                tagged,
                ...rest
            } = main;
            return rest;
        });
        out = [...out, rest, ...sidecar];
        return out;
    }, []);

    await download.toNdJson(list, output.data + '/posts.jsonl');

    if (process.env.INSTAGRAM_IMAGES === 'true') {
        await download.assets(content, output.images);
    }

    const children = content.reduce((out, item) => {
        out = [...out, ...item.children];
        return out;
    }, []);

    if (process.env.INSTAGRAM_IMAGES === 'true') {
        await download.assets(children, output.images);
    }

    return content;
}

async function collectPosts(content, session, output, next = null) {

    if (!next) {
        next = session.count.shift();
    }

    const gql = await pull.request({
        url: next,
        headers: session.headers
    });

    const userPosts = await extractPostDetails(gql.items, output);

    content.posts = [...content.posts, ...userPosts];

    const limit = Number(process.env.INSTAGRAM_POSTS_LIMIT) ? ((content.posts.length > Number(process.env.INSTAGRAM_POSTS_LIMIT)) ? true : false) : false;

    if (!limit) {
        console.log('User: ' + content.username + ' - ' + content.id + ' posts: ' + content.postsCount + ' - ' + (content.posts.length) + ' - ' + percent(content.posts.length).of(content.postsCount).toFixed(1) + '%');
    } else {
        console.log('User: ' + content.username + ' - ' + content.id + ' posts: ' + content.postsCount + ' - ' + (content.posts.length) + ' - ' + percent(content.posts.length).of(content.postsCount).toFixed(1) + `% - Limit reached: ${process.env.INSTAGRAM_POSTS_LIMIT} posts`);
    }

    await timeout(randomInt(500, 1000));

    if (gql.more_available && !limit) {
        return collectPosts(content, session, output, `${next}&max_id=${gql.next_max_id}`);
    }

    const {
        posts,
        ...profile
    } = content;

    const mergedPosts = content.posts.reduce((out, item) => {
        const {
            children,
            tagged,
            ...rest
        } = item;
        const sidecar = item.children.map(main => {
            const {
                tagged,
                ...rest
            } = main;
            return rest;
        });
        out = [...out, rest, ...sidecar];
        return out;
    }, []);

    await kml.generate(mergedPosts.sort((a, b) => b.likesCount - a.likesCount), output.data + '/locations.kml');

    const mergedTags = content.posts.reduce((out, item) => {
        const current = item.tagged.map(main => {
            main.id = item.id;
            return main;
        });
        out = [...out, ...current];
        return out;
    }, []);

    await download.toNdJson(mergedTags, output.data + '/tagged.jsonl');

    return {
        profile,
        posts: mergedPosts,
        tagged: mergedTags
    };

}

function getEntities(data) {
    if (data.entities.length) {
        return data.entities.map(item => (item.user ? `https://www.instagram.com/${item.user.username}/` : '')).filter(item => item).join(', ').trim()
    }
    return '';
}

async function getProfiles(data, session, output, total = null, noaccount = 0, out = []) {

    if (!total) {
        total = data.length;
    }

    const target = data.shift();

    const res = await pull.request({
        url: `https://i.${process.env.INSTAGRAM_HOST}/api/v1/users/web_profile_info/?username=${target.username}`,
        headers: session.headers
    });

    let profile = {}

    if (res.data && !res.data.user && res.status === 'ok') {

        console.log('User does not exists: ' + target.username);

        noaccount = noaccount + 1;

        await download.toNdJson([{
            username: target.username,
            groupId: target.groupId
        }], output.data + '/noaccount.jsonl');

    } else {

        const user = res.data.user;

        profile = {
            id: user.id,
            fbid: user.fbid,
            biography: user.biography,
            externalUrl: user.external_url,
            subscribersCount: user.edge_followed_by.count,
            subscribtions: user.edge_follow.count,
            fullName: user.full_name,
            highlightReelCount: user.highlight_reel_count,
            isBusinessAccount: user.is_business_account,
            businessContact: user.business_contact_method,
            isRecentUser: user.is_joined_recently,
            businessCategoryName: user.business_category_name,
            categoryName: user.category_name,
            linkedFacebookPage: user.connected_fb_page,
            isPrivate: user.is_private,
            isVerified: user.is_verified,
            transparencyLabel: user.transparency_label,
            transparencyProduct: user.transparency_product,
            username: user.username,
            postsCount: user.edge_owner_to_timeline_media.count,
            groupId: target.groupId
        };

        out.push(profile);

        console.log('User: ' + profile.username + ' - ' + profile.id + ' profile: ' + total + ' - ' + (out.length + noaccount) + ' - ' + percent(out.length + noaccount).of(total).toFixed(1) + '%');

        await download.toNdJson([profile], output.data + '/profiles.jsonl');

    }

    if (data.length) {
        return getProfiles(data, session, output, total, noaccount, out);
    }

    return out;
}

async function profiles(data) {
    const start = process.hrtime();

    const [first] = data;

    const cookiePath = path.resolve(__dirname, '../cookies.json');

    const availableCookies = await outcome(fs.access(cookiePath, constants.R_OK | constants.W_OK));

    const cookie = (availableCookies.success) ? JSON.parse(await fs.readFile(cookiePath)) : [];

    const session = await auth.get(first.username, cookie);

    if (session.error) {
        return session;
    }

    await fs.writeFile(cookiePath, JSON.stringify(session.cookies));

    const output = {
        data: path.resolve(__dirname, `../data/profiles`)
    };

    await mkdirp(output.data);

    const profiles = await getProfiles(data, session, output);

    const end = process.hrtime(start);
    console.log('Done in ' + prettyHrtime(end));

    return {
        data,
        output,
        profiles
    };
}

async function getUserData(target) {

    const start = process.hrtime();

    const cookiePath = path.resolve(__dirname, '../cookies.json');

    const availableCookies = await outcome(fs.access(cookiePath, constants.R_OK | constants.W_OK));

    const cookie = (availableCookies.success) ? JSON.parse(await fs.readFile(cookiePath)) : [];

    const session = await auth.get(target, cookie);

    if (session.error) {
        return session;
    }

    if (!availableCookies.success) {
        await fs.writeFile(cookiePath, JSON.stringify(session.cookies));
    }

    const output = {
        data: path.resolve(__dirname, `../data/${target}`),
        images: path.resolve(__dirname, `../data/${target}/images`)
    };

    await mkdirp(output.data);
    await mkdirp(output.images);

    const res = await pull.request({
        url: `https://i.${process.env.INSTAGRAM_HOST}/api/v1/users/web_profile_info/?username=${target}`,
        headers: session.headers
    });

    const user = res.data.user;

    console.log('User: ' + user.username + ' - ' + user.id + ' profile');

    const content = {
        id: user.id,
        fbid: user.fbid,
        biography: user.biography,
        entities: getEntities(user.biography_with_entities),
        externalUrl: user.external_url,
        subscribersCount: user.edge_followed_by.count,
        subscribtions: user.edge_follow.count,
        fullName: user.full_name,
        highlightReelCount: user.highlight_reel_count,
        isBusinessAccount: user.is_business_account,
        businessContact: user.business_contact_method,
        isRecentUser: user.is_joined_recently,
        businessCategoryName: user.business_category_name,
        categoryName: user.category_name,
        linkedFacebookPage: user.connected_fb_page,
        isPrivate: user.is_private,
        isVerified: user.is_verified,
        profilePic: user.profile_pic_url,
        profilePicHD: user.profile_pic_url_hd,
        file: path.basename(url.parse(user.profile_pic_url_hd).pathname),
        transparencyLabel: user.transparency_label,
        transparencyProduct: user.transparency_product,
        username: user.username,
        postsCount: user.edge_owner_to_timeline_media.count,
        posts: []
    };

    if (process.env.INSTAGRAM_IMAGES === 'true') {
        await download.assets([content], output.images);
    }

    const {
        posts,
        ...profile
    } = content;

    await download.toNdJson([profile], output.data + '/profile.jsonl');

    let core = {};

    if (session.count.length) {
        core = await collectPosts(content, session, output);
    }

    core.output = output;

    const end = process.hrtime(start);
    console.log('Done in ' + prettyHrtime(end));

    return core;

}

module.exports = {
    profiles,
    getUserData
};