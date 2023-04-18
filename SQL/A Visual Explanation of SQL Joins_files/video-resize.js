//
// resize video embeds to fit fluid layouts
//


// when the entire webpage is fully loaded...
document.addEventListener('DOMContentLoaded', function() {
       
    resizeVideos();

    // also, when the window is resized, do it again
    $(window).resize(function() {
        resizeVideos();
    })

}, false);

function resizeVideos() {
    // is jQuery loaded?
    if(window.jQuery) {               
        resizeVideosInner(); 
    } else {
        // if not, wait and try again
        window.setTimeout(resizeVideos, 250);
    }    
}

function resizeVideosInner() {
    // The element that is fluid width
    var $fluidEl = $(".post-content");
    // Find all YouTube videos within this element
    var $allVideos = $("iframe[src*='//www.youtube.com/embed/']");

    var newWidth = $fluidEl.width();
    // Resize all videos according to their own aspect ratio
    $allVideos.each(function() {
        var $el = $(this);
        if ($el.height != "")
        {
            $el
            // retain the original aspect ratio
            .data('aspectRatio', this.height / this.width)
            // and remove the hard coded width/height
            .removeAttr('height')
            .removeAttr('width');
        }        
        $el.width(newWidth).height(newWidth * $el.data('aspectRatio'));
    });
}