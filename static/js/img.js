if (!String.prototype.startsWith) {
    String.prototype.startsWith = function(searchString, position) {
        position = position || 0;
        return this.indexOf(searchString, position) === position;
    };
}

new Dropzone(document.getElementById("uploadButton"), {
    url: "post",
    previewsContainer: false,
    init: function() {
        this.on("success", function(file, response){
            if (response.startsWith('v/')){
                window.location.assign('/');//response);
            } else {
                alert('Error: ' + response);
            }
        });
    }
});

new Dropzone(document.body, {
    url: "post",
    previewsContainer: false,
    clickable: false,
    init: function() {
        this.on("success", function(file, response){
            if (response.startsWith('v/')){
                window.location.assign('/');//response);
            } else {
                alert('Error: ' + response);
            }
        });
    }
});
