'use strict';

/**
 * mention service.
 */

const { createCoreService } = require('@strapi/strapi').factories;

module.exports = createCoreService('api::mention.mention');
