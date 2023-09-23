<div align="center">
<!-- TODO: add link to website once it is ready -->
<h1>
    GETPOS
</h1>
Simple, yet powerful POS solutions for businesses
</div>

## Introduction

A cloud-based Get POS solution is a computerized system designed for your retail store, restaurant, multi-store, and supermarket to manage transactions, orders, inventory, and in-store product sales in one go. 

This custom POS system is built to increase revenue and save time for every retail and hospitality business chain that offers multi-location features such as inventory transfers, network pricing, and advanced reports.

It builds on top of [ERPNext](https://github.com/frappe/erpnext) and the [Frappe Framework](https://github.com/frappe/frappe) - incredible FOSS projects built and maintained by the incredible folks at Frappe. Go check these out if you haven't already!

## Key Features
- Offline Syncing
- Inventory Management
- Order Management
- Employee Management
- Supplier Management
- Reporting
- Accounts & Payroll
- Multi-location Management

For a detailed overview of these features, please [refer to the documentation](https://wiki.nestorbird.com/wiki/get-pos).

## Installation

#### Frappe Cloud
Simply signup with Frappe Cloud for a free trial and create a new site. Select Frappe Version-14 and select ERPNext and getPOS from Apps to Install. You can get started in a few minutes with a new site and a fresh install to try out the simple and cool features of the App.


#### Manual Installation (Self hosted)

Once you've [set up a Frappe site](https://frappeframework.com/docs/v14/user/en/installation/), installing GETPOS is simple:

1. Download the app using the Bench CLI.

    ```bash
    bench get-app --branch [branch name] https://github.com/nestorbird/GETPOS.git
    ```

    Replace `[branch name]` with the appropriate branch as per your setup:

    | Frappe Branch | GETPOS Branch           |
    |---------------|-------------------------|
    | version-14    | production              |
    | version-13    | production              |
    | develop       | deployment-development  |

    If it isn't specified, the `--branch` option will default to `deployment-development`.

2. Install the app on your site.

    ```bash
    bench --site [site name] install-app nbpos
    ```

### App Downloads
The mobile and tablet applications. 
1. [Android POS Agent App](https://bit.ly/getposapp)
2. [iOS POS Agent App](https://bit.ly/getposiosapp)

## Contributing
- [Issue Guidelines](https://github.com/frappe/erpnext/wiki/Issue-Guidelines)
- [Pull Request Requirements](https://github.com/frappe/erpnext/wiki/Contribution-Guidelines)

## License
[GNU General Public License (v3)](https://github.com/ashishsaretia/GETPOS/blob/deployment-development/license.txt)

## Support
For support please visit or click [here](https://wiki.nestorbird.com/wiki/support)