import fetch from 'isomorphic-fetch';
import tv4 from 'tv4';

export const INIT_DATA_START = 'INIT_DATA_START';
export const INIT_DATA_SUCCESS = 'INIT_DATA_SUCCESS';
export const INIT_DATA_ERROR = 'INIT_DATA_ERROR';
export const AUTHORING_SELECT_CHANNEL = 'AUTHORING_SELECT_CHANNEL';
export const AUTHORING_SELECT_LOCALE = 'AUTHORING_SELECT_LOCALE';
export const AUTHORING_SELECT_TYPE = 'AUTHORING_SELECT_TYPE';
export const LOAD_DISTRIBUTION_FILE_START = 'LOAD_DISTRIBUTION_FILE_START'
export const LOAD_DISTRIBUTION_FILE_ERROR = 'LOAD_DISTRIBUTION_FILE_ERROR';
export const LOAD_DISTRIBUTION_FILE_SUCCESS = 'LOAD_DISTRIBUTION_FILE_SUCCESS';
export const AUTHORING_PUBLISH_START = 'AUTHORING_PUBLISH_START';
export const AUTHORING_PUBLISH_SUCCESS = 'AUTHORING_PUBLISH_SUCCESS';
export const AUTHORING_PUBLISH_ERROR = 'AUTHORING_PUBLISH_ERROR';

function requestInitData() {
  return {
    type: INIT_DATA_START
  };
}

function receiveInitData(data) {
  return {
    type: INIT_DATA_SUCCESS,
    env: data.d.env,
    channels: data.d.chans,
    distributions: data.d.dists,
    schema: data.d.schema,
    receivedAt: Date.now()
  };
}

function initDataError(message) {
  return {
    type: INIT_DATA_ERROR,
    message: 'Initialization failed. Refresh to try again. Error: ' + message
  };
}

function fetchInitData(state) {
  return dispatch => {
    dispatch(requestInitData());
    return fetch(state.initData.url)
      .then(function(response){
        if (response.status >= 200 && response.status < 300) {
          response.json().then(json => dispatch(receiveInitData(json)))
        } else {
          dispatch(initDataError(response.statusText));
        }
      });
  };
}

function shouldFetchInitData(state) {
  if (state.initData.isLoaded || state.initData.isFetching) {
    return false;
  }
  return true;
}

export function fetchInitDataIfNeeded() {
  return (dispatch, getState) => {
    if (shouldFetchInitData(getState().Authoring)) {
      return dispatch(fetchInitData(getState().Authoring));
    }
  };
}

export function selectChannel(channel) {
  return {
    type: AUTHORING_SELECT_CHANNEL,
    channel
  };
}

export function selectLocale(locale) {
  return {
    type: AUTHORING_SELECT_LOCALE,
    locale
  };
}

export function selectType(tileType) {
  return {
    type: AUTHORING_SELECT_TYPE,
    tileType
  };
}

export function loadDistributionFile(file) {
  return (dispatch, getState) => {
    var reader = new FileReader();

    reader.onerror = (e) => {
      dispatch((() => ({
        type: LOAD_DISTRIBUTION_FILE_ERROR,
        message: 'Error loading file.'
      }))());
    };

    reader.onload = () => {
      // Parse the file (JSON).
      try {
        var data = JSON.parse(reader.result);
      } catch(e) {
        dispatch((() => ({
          type: LOAD_DISTRIBUTION_FILE_ERROR,
          message: 'Error parsing file. Verify that it is valid JSON.'
        }))());
        return;
      }

      // Validate the schema.
      var distributions = {};
      var assets = {};
      var schema = getState().Authoring.initData.schema;
      if (data.hasOwnProperty('assets')) {
          schema = schema.compact;
          distributions = data.distributions;
          assets = data.assets;
      } else {
          schema = schema.default;
          distributions = data;
      }
      var results = tv4.validateResult(data, schema);

      if (!results.valid) {
        dispatch((() => ({
          type: LOAD_DISTRIBUTION_FILE_ERROR,
          message: 'Validation failed: ' + results.error.message + ' at ' + results.error.dataPath
        }))());
        return;
      }

      // Process the tiles.
      var tiles = separateTilesTypes(distributions, assets);

      // And that's all folks. Let the World know.
      dispatch((() => ({
        type: LOAD_DISTRIBUTION_FILE_SUCCESS,
        tiles: tiles
      }))());
    };

    dispatch((() => ({type: LOAD_DISTRIBUTION_FILE_START}))());
    reader.readAsText(file);
  };
}

// Helper for processing distribution files
function separateTilesTypes(data, assets) {
  // Separate Tiles types from a list of tiles in 2 groups: suggested, directory
  var output = {raw: data, ui: {}};

  for (var locale in output.raw) {
    var tiles = data[locale];

    output.ui[locale] = {
      suggestedTiles: [],
      directoryTiles: []
    };

    for (var i = 0; i < tiles.length; i++) {
      var tile = tiles[i];

      // populate the imageURI and enhancedImageURI if tile is in compact format
      if (tile.hasOwnProperty('imageURI') && assets.hasOwnProperty(tile.imageURI)) {
        tile.imageURI = assets[tile.imageURI];
      }
      if (tile.hasOwnProperty('enhancedImageURI') && assets.hasOwnProperty(tile.enhancedImageURI)) {
        tile.enhancedImageURI = assets[tile.enhancedImageURI];
      }
      if (tile.frecent_sites) {
        output.ui[locale].suggestedTiles.push(tile);
      }
      else {
        output.ui[locale].directoryTiles.push(tile);
      }
    }
  }

  return output;
}

export function publishDistribution() {
  return (dispatch, getState) => {
  /**
   * Send tiles to backend for publication.
   * Assumes data is correct.
   */
   dispatch((() => ({type: AUTHORING_PUBLISH_START}))());

   var state = getState().Authoring;
   var compressedTiles = compressPayload(state.distribution.tiles.raw);
   var scheduled = state.distribution.scheduled;
   var channelId = state.initData.channels.find((element, index, array) => {return element.name === state.selectedChannel;}).id;

   // TODO: reimplement code with fetch

  // spliceData.postTiles(compressPayload(tiles.raw), $scope.channelSelect.id, $scope.deployConfig)
  //   .success(function(data) {
  //     var deployed = data.deployed;
  //     var msg = '<ol>';
  //     for (var url of data.urls) {
  //
  //       var uploadStatus = "cached";
  //       var uploadClass = "text-muted";
  //
  //       if (url[1] == true) {
  //         uploadStatus = "new";
  //         uploadClass = "text-success";
  //       }
  //
  //       msg += '<li><strong class="' + uploadClass + '">' + uploadStatus + '</strong> <a href="' + url[0] + '">' + url[0] + '</a> </li>';
  //     }
  //     msg += '</ol>';
  //     $scope.uploadMessage = {
  //       success: true,
  //       deployed: deployed,
  //       msg: msg
  //     };
  //
  //     var urls = data.urls;
  //     $scope.deployConfig.now = false;
  //     $scope.clearScheduledDate();
  //     $scope.refreshDistributions();
  //   })
  //   .error(function(data, status, headers, config, statusText) {
  //     var errors = data.err;
  //     var msg = '<ol>';
  //     if (errors != null) {
  //       for (var error of errors) {
  //         if (error.path) {
  //           msg += "<li>In <strong>" + error.path + "</strong>: " + error.msg + "</li>";
  //         }
  //         else {
  //           msg += "<li>" + error.msg + "</li>";
  //         }
  //       }
  //     }
  //     msg += "</ol>";
  //     $scope.uploadMessage = {
  //       success: false,
  //       status: status,
  //       statusText: statusText,
  //       msg: msg,
  //     };
  //   }).finally(function() {
  //     $scope.uploadInProgress = false;
  //     $scope.uploadModal.$promise.then($scope.uploadModal.show);
  //   });
  };
};

// Helper for publishing tiles
function cloneTile(tile) {
  var copy = JSON.parse(JSON.stringify(tile));
  return copy;
};

// Helper for publishing tiles
function compressPayload(tiles) {
  /* *
   * compress the payload for publishing. Note that the tiles might be cached,
   * therefore we create a copy here
   */
  var copies = {};
  var uri2id = {};
  var assets = {};
  var id = 0;

  for (var locale in tiles) {
    copies[locale] = [];
    var locale_tiles = tiles[locale];
    for (var i = 0, len = locale_tiles.length; i < len; i++) {
      var tile = locale_tiles[i];
      var imageURI = tile.imageURI;
      var copy = cloneTile(tile);

      copies[locale].push(copy);
      if (imageURI in uri2id) {
        copy.imageURI = uri2id[imageURI];
      } else {
        uri2id[imageURI] = copy.imageURI = id.toString();
        id++;
      }
      if (tile.hasOwnProperty('enhancedImageURI')) {
        imageURI = tile.enhancedImageURI;
        if (imageURI in uri2id) {
          copy.enhancedImageURI = uri2id[imageURI];
        } else {
          uri2id[imageURI] = copy.enhancedImageURI = id.toString();
          id++;
        }
      }
    }
  }

  for (var uri in uri2id) {
    if (uri2id.hasOwnProperty(uri)) {
      assets[uri2id[uri]] = uri;
    }
  }

  return {
    assets,
    distributions: copies
  };
};
