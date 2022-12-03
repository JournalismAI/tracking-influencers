'use strict';

/**
 * search service
 */

const { createCoreService } = require('@strapi/strapi').factories;

module.exports = createCoreService('api::search.search');
