# DMac Website Deployment Guide

This guide will help you deploy the DMac website to Netlify for your AI conference presentation.

## Prerequisites

- A Netlify account (free tier is sufficient)
- The DMac website files (located in the `website` directory)

## Deployment Steps

### Option 1: Manual Deployment (Recommended for Quick Setup)

1. **Sign up for Netlify**
   - Go to [netlify.com](https://netlify.com)
   - Sign up for a free account (you can use your GitHub, GitLab, or Bitbucket account)

2. **Deploy the Website**
   - From the Netlify dashboard, click on "Sites"
   - Click the "Add new site" button and select "Deploy manually"
   - Drag and drop the entire `website` folder onto the designated area
   - Wait for the upload and deployment to complete (usually takes less than a minute)

3. **Configure the Site**
   - Once deployed, click on "Site settings"
   - Under "Site information", click "Change site name"
   - Enter a custom subdomain (e.g., `dmac-ai`)
   - Your site will be available at `dmac-ai.netlify.app`

### Option 2: Deployment via GitHub

1. **Push the Website to GitHub**
   - Create a new GitHub repository
   - Push the website files to the repository

2. **Connect Netlify to GitHub**
   - From the Netlify dashboard, click on "Sites"
   - Click the "Add new site" button and select "Import an existing project"
   - Select GitHub as the Git provider
   - Authenticate with GitHub and select your repository
   - Configure the build settings:
     - Base directory: Leave blank or set to the directory containing the website files
     - Build command: Leave blank (no build step needed)
     - Publish directory: Leave blank or set to the directory containing the website files
   - Click "Deploy site"

3. **Configure the Site**
   - Follow the same steps as in Option 1 to configure the site name

## Verifying the Deployment

1. **Check the Site**
   - Visit your Netlify site URL (e.g., `dmac-ai.netlify.app`)
   - Verify that all pages, images, and functionality work correctly
   - Test the site on different devices and browsers

2. **Generate QR Code**
   - Use the QR code provided in the `images/qr-code.svg` file
   - Alternatively, generate a new QR code using a service like [QR Code Generator](https://www.qr-code-generator.com/)
   - The QR code should point to your Netlify site URL

## Troubleshooting

- **Missing Images**: Make sure all image paths are correct and the images are included in the deployment
- **Styling Issues**: Verify that the CSS file is properly linked and loaded
- **JavaScript Errors**: Check the browser console for any JavaScript errors
- **404 Errors**: Ensure all file paths are correct and the files exist

## Conference Presentation Tips

- **Pre-load the Site**: Open the site before your presentation to ensure it's cached
- **Have a Backup**: Keep a local copy of the site open in case of internet issues
- **Test the QR Code**: Make sure the QR code works and redirects to your site
- **Prepare for Questions**: Be ready to explain the technology behind the site

## After the Conference

- **Gather Feedback**: Ask attendees for feedback on the website
- **Update the Site**: Make improvements based on feedback
- **Share the Link**: Share the site URL with interested parties

For any issues or questions, refer to the [Netlify documentation](https://docs.netlify.com/) or contact the DMac development team.
