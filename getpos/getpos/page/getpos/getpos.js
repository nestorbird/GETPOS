frappe.pages['getpos'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'GETPOS',
        single_column: true
    });
    // Function to create heading
    function createHeading() {
        var heading = $('<div>').addClass('heading');
        var instructionsButton = $('<button>')
            .text('Instructions')
            .addClass('instruction-button')
            .click(function() {
                $('.instructions-content').toggle();
                $('.about-content').hide();
            });
        var aboutButton = $('<button>')
            .text('About')
            .addClass('about-button')
            .click(function() {
                $('.about-content').toggle();
                $('.instructions-content').hide();
            });
        heading.append(instructionsButton).append(aboutButton);
        $(page.body).prepend(heading);
    }
    // Call heading creation function
    createHeading();
    // Create div elements for instructions and about content
    var instructionsContent = $('<div>').addClass('instructions-content').hide().appendTo(wrapper);
    var aboutContent = $('<div>').addClass('about-content').hide().appendTo(wrapper);
    // Set instructions content
    instructionsContent.html(`
        <div class="instruction-wrapper">      
            <h2>How to Use the Get POS App?</h2>
            <h3>Instructions</h3>
            <ol>     
                <li>Install Get POS App: Download it from the Google Play Store (Android) or the Apple App Store (iOS).</li>
                <ul>
                    <li>Android Users: Search "Get POS App" in the Google Play Store, and tap "Install." <br> Download Now: <a href="https://play.google.com/store/apps/details?id=com.nestorbird.nb_pos">Android App Link</a></li>
                    <li>iOS Users: Search "Get POS App" in the App Store, and tap “Install.” <br> Download Now: <a href="https://apps.apple.com/in/app/get-pos/id1605092754">iOS App Link</a></li>
                </ul>
                <li>Get POS App: Tap the app icon on your device's home screen.</li>
                <li>Sign In or Sign Up: Use existing credentials or create a new account.</li>
                <li>Explore Features: Get to know all about adding products, managing inventory, processing transactions, etc.</li>
                <li>Customize Settings: Adjust tax rates, payment methods, receipt formats, etc., as needed.</li>
                <li>Start Using: Begin managing your point-of-sale operations efficiently.</li>
            </ol>
        </div>
    `);
    // Set about content
    aboutContent.html(`
        <div class="about-wrapper">
            <h3>About</h3>
            <p>GETPOS Logo</p>
        <img src="https://play-lh.googleusercontent.com/quOMsHgYGvjboFOgE92wXNR9Z5KlfjBrxstqJU17ggns-OnC3pEa5zvJ3Na0MP6-hAbk=w240-h480-rw" alt="GET POS Logo">
        <br> <br>
        <p>GET POS: India’s Leading Offline POS App For Inventory and Order Management</p>
        <p>NestorBird Get POS App: India’s leading offline app features built-in functionalities to integrate with multiple ERP software.</p>
        <p>This cloud-based Get POS solution is a computerized system designed for your retail store, restaurant, multi-store,and supermarket to manage
        transactions,<br> orders, inventory, and in-store product sales in one go. Get POS app has several amazing features, such as Inventory Management, Order Management, Offline Syncing,<br> Accounting, Vendor Management, HRM, Reports, Selling, Buying, and more.</p>
        <h4>Contact Us</h4>
        <p>Email Address:</p>
        <ul>
            <li>(Sales) - sales@nestorbird.com</li>
            <li>(Support) - support@nestorbird.com</li>
            <li>(General) - info@nestorbird.com</li>
        </ul>
        <p>Contact No: +91-9878990102</p>
        </div>
    `);
    // Custom CSS styles
    var customStyles = `
        .heading {
            background-color: #F8F9FA;
            border-radius: 200px;
            border: 1px solid black;
        }
        .instruction-button, .about-button {
            color: #000000;
            border: none;
            border-radius: 10px;
            padding: 10px 20px;
            margin-right: 10px;
            cursor: pointer;
            outline: none;
            margin-left: 1vw;
            font-weight:bold;
            font-size:1.7vw;
        }
        .instruction-button:hover, .about-button:hover {
            background-color: #C7CED6;
        }
        .instruction-wrapper {
            margin-left:170px;
            margin-top: 30px;
            background-color:#f0f8ff;
            width:75vw;
        }
        .about-wrapper{
            margin-left:170px;
            margin-top: 10px;
            background-color:#f0f8ff;
            width:75vw;
        }
    `;
    // Append custom styles to the page
    $('head').append(`<style>${customStyles}</style>`);
}