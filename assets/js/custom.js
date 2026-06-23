jQuery(document).ready(function ($) {
    $("#imageUpload").change(function () {
        readURL(this);
    });

    function readURL(input) {
        if (input.files && input.files[0]) {
            var reader = new FileReader();
            reader.onload = function (event) {
                $("#uploadedImage").attr("src", event.target.result);
            };
            reader.readAsDataURL(input.files[0]);
            $(".image-preview").show();
        }
    }

    function drawCircularImage(ctx, image, x, y, radius) {
        var scaleFactor = Math.max(2 * radius / image.width, 2 * radius / image.height);
        var scaledWidth = image.width * scaleFactor;
        var scaledHeight = image.height * scaleFactor;
        var offsetX = x - (scaledWidth - 2 * radius) / 2;
        var offsetY = y - (scaledHeight - 2 * radius) / 2;

        ctx.save();
        ctx.globalCompositeOperation = "destination-over";
        ctx.drawImage(image, offsetX, offsetY, scaledWidth, scaledHeight);
        ctx.restore();
    }

    $("#generateButton").click(function () {
        var imageSrc = $("#uploadedImage").attr("src");
        var cardTemplate = new Image();
        cardTemplate.src = "/wp-content/uploads/2023/11/fb-profile-652px.png";

        cardTemplate.onload = function () {
            var canvas = document.createElement("canvas");
            canvas.width = cardTemplate.width;
            canvas.height = cardTemplate.height;
            var ctx = canvas.getContext("2d");
            ctx.drawImage(cardTemplate, 0, 0);

            var image = new Image();
            image.src = imageSrc;
            image.onload = function () {
                drawCircularImage(ctx, image, 0, 0, 330);
                var downloadLink = document.createElement("a");
                downloadLink.href = canvas.toDataURL("image/png");
                downloadLink.download = "filled_profile.png";
                downloadLink.click();
            };
        };
    });

    function adjustProperties() {
        var windowWidth = $(window).width();
        var imageWidth = 652;
        var imageHeight = 652;
        var ratio = windowWidth / imageWidth;

        if (windowWidth < 768) {
            $(".img_upload span").css({ "font-size": (31 * ratio) + "px" });
            $(".img_gen #name").css({ "font-size": (40 * ratio) + "px" });
            $(".img_gen #designation").css({ "font-size": (30 * ratio) + "px" });
            $(".img_gen #company").css({ "font-size": (30 * ratio) + "px" });
        }

        var widthUpload = 100 * ratio;
        var topPositionName = 450 * ratio;
        var leftPositionName = 50 * ratio;
        var topPositionDesignation = 400 * ratio;
        var leftPositionDesignation = 78 * ratio;
        var topPositionCompany = 437 * ratio;
        var leftPositionCompany = 78 * ratio;

        $(".img_gen .image-preview").css({
            "width": widthUpload + "%",
            "height": (100 * ratio * (imageHeight / imageWidth)) + "%",
            "top": "0%",
            "left": "0%"
        });
        $(".img_gen #name").css({
            "font-size": (40 * ratio) + "px",
            "top": topPositionName + "px",
            "left": leftPositionName + "px"
        });
        $(".img_gen #designation").css({
            "font-size": (30 * ratio) + "px",
            "top": topPositionDesignation + "px",
            "left": leftPositionDesignation + "px"
        });
        $(".img_gen #company").css({
            "font-size": (30 * ratio) + "px",
            "top": topPositionCompany + "px",
            "left": leftPositionCompany + "px"
        });
    }

    if ($(window).width() < 768) {
        adjustProperties();
    }

    $(window).on("resize", function () {
        if ($(window).width() < 768) {
            adjustProperties();
        }
    });
});
