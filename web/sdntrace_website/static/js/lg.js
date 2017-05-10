/* Initial configuration */
var _initial_configuration = function() {
    if (typeof SDNLG_CONF != 'undefined') {
        // header logo img src
        $('#header__logo img').attr("src", SDNLG_CONF.header_logo_img_src);
        // header name
        // $('#header__name').text(SDNLG_CONF.header_name);
        // SDN LG version
        $('#about__version').text(SDNLG_CONF.version);
        $('#about__roadmap').html(SDNLG_CONF.about_roadmap);
    }
}

/* Initial load */
$(function() {
    // Load js configuration data
    _initial_configuration();
});


/**
 * Helper function to remove duplicates from an array.
 */
function array_unique_fast(a) {
    var seen = {};
    var out = [];
    var len = a.length;
    var j = 0;
    for(var i = 0; i < len; i++) {
         var item = a[i];
         if(seen[item] !== 1) {
               seen[item] = 1;
               out[j++] = item;
         }
    }
    return out;
}

/**
 *
 */
function format_speed (speed) {
    if (speed % 1000000000 >= 0) {
        return (speed / 1000000000) + "GB";
    } else if (speed % 1000000 >= 0) {
        return (speed / 1000000) + "MB";
    } else if (speed % 1000 >= 0) {
        return (speed / 1000) + "KB";
    }
}
