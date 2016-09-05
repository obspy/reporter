$(window).load(function() {

    console.log($("#feed"));
    GitHubActivity.feed({
        username: "obspy",
        repository: "obspy", // optional
        selector: "#github-feed",
        limit: 20 // optional
    });

    $(".twentytwenty-container").twentytwenty();

});
