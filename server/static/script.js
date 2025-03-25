function main()
{
    // Create a browser fingerprint, used simply to assign an arbitrary User context to different browser sessions
    // https://github.com/fingerprintjs/fingerprintjs
    let usercontext;
    let ldClient;
    const fpPromise = import('https://openfpcdn.io/fingerprintjs/v4')
      .then(FingerprintJS => FingerprintJS.load());
    var visitorId = ''
    // Get the visitor identifier when you need it.
    fpPromise
      .then(fp => fp.get())
      .then(result => {
        // This is the visitor identifier:
        visitorId = result.visitorId;
        // Call API to get unique user context object for this browser session
        return fetch(`/api/getContext/${encodeURIComponent(visitorId)}`)
            .then(response => response.json())
            .then(user_context => {
                usercontext = user_context;
                console.log(usercontext);
                // Initialize LaunchDarkly
                ldClient = LDClient.initialize(ldClientId, usercontext); // Initialize LaunchDarkly client

                // Render initial page view and subscribe for changes to CommentFeature flag
                ldClient.on('ready', render); // Once LaunchDarkly client is ready, start to build the page
                ldClient.on('change', (settings) => { // Subscribe to changes to dynamically update page with comment feature without refreshing
                    var selector = dropdown.querySelector('select');
                 renderComments(selector.value);
                });
            });
      })




    const flagKey = 'candy-comments'; // identify the key to be referenced to enable comment feature
    const dropdown = document.getElementById('candy-list-dropdown');
    const select = document.createElement('select');
    const option = document.createElement('option');
    const candyDetailsDiv = document.getElementById('candy-details');
    const candyImageDiv = document.getElementById('candy-image');
    const commentSection = document.getElementById('comment-section');
    const welcomeDiv = document.getElementById('welcome');
    const rendered = false;

    function stringify_date(date) {
        const months = ["January", "February", "March", "April", "May", "June",
                       "July", "August", "September", "October", "November", "December"];
        const monthName = months[date.getUTCMonth()];
        const day = date.getUTCDate();
        const year = date.getUTCFullYear();

        return `${monthName} ${day}, ${year}`;
    }

    function render() { // Do the initial rendering of elements
        if (!rendered) {
            var utcSeconds = usercontext.user_since;
            var d = new Date(0);
            d.setUTCSeconds(utcSeconds);
            welcomeDiv.innerHTML=`
              <p>Welcome ${usercontext.name}!</p>
              <p>User Since: ${stringify_date(d)}</p>`
            fetch('/api/fetch/candy_names')  // use server API to list candy names and add them to dropdown
                .then(response => response.json())
                .then(names => {
                    option.value = 'NULL';
                    option.textContent = 'Select...';
                    select.appendChild(option);
                    names.forEach(name => {
                        const option = document.createElement('option');
                        option.value = name;
                        option.textContent = name;
                        select.appendChild(option);
                    });
                    dropdown.appendChild(select);

                    select.addEventListener('change', handleCandySelection);  // define action for when item is selected
                })
                .catch(error => {
                    console.error("Error fetching strings:", error);
                });
            }

        function handleCandySelection(event) {
            const selectedCandy = event.target.value;
            console.log(visitorId);
            fetch(`/api/fetch/${encodeURIComponent(selectedCandy)}`) // user server API to get the details of selected candy
                .then(response => response.json())
                    .then(data => {
                        // Format the data into the Details box
                        candyDetailsDiv.innerHTML = `
                            <p>Name: ${data.name}</p>
                            <p>Type: ${data.type}</p>
                            <p>Components: ${data.components}</p>
                        `;
                        candyImageDiv.innerHTML = `<img src="/static/${data.image}" alt="${data.name}">`; // Display image
                    });
                renderComments(selectedCandy); // attempt to display comments

        }

    }
    function renderComments(candyName) {
        const candyCommentsEnabled = ldClient.variation(flagKey, false); // get state of feature flag
        if (candyCommentsEnabled && candyName !== 'NULL') { // if featureflag is True, display comments
            fetch(`/api/comments/${encodeURIComponent(candyName)}`)
                .then(response => response.json())
                .then(comments => {
                    let commentsHtml = `
                        <h3>Submit a Comment</h3>
                        <form id="comment-form">
                            <textarea id="comment-text"></textarea>
                            <button type="submit">Submit</button>
                        </form>
                        <h4> Previous Comments</h4>
                        <div id="comments-list">
                    `;
                    comments.reverse().forEach(comment => {
                        commentsHtml += `<p>* ${comment}</p>`;
                    });
                    commentsHtml += `</div>`;
                    commentSection.innerHTML = commentsHtml;

                    document.getElementById('comment-form').addEventListener('submit', (event) => {
                        event.preventDefault();
                        const commentText = document.getElementById('comment-text').value;
                        fetch(`/api/comments/${encodeURIComponent(candyName)}`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ comment: commentText})
                        }).then(() => {
                            renderComments(candyName);
                        });
                });
            });
        }
        else { //leave section blank if feature flag is not True
            commentSection.innerHTML = '';
        }
    }


}
main();