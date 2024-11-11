// Import necessary modules
const { chromium } = require('playwright'); // Import Playwright for browser automation
const fs = require('fs'); // Import filesystem module for file operations
const path = require('path'); // Import path module to handle file paths

// Array of LinkedIn profile URLs to scrape
const profilesToScrape = [
  'https://www.linkedin.com/in/sparsh-tiwari-222739250/',
  'https://www.linkedin.com/in/vedansh-sood-051b10165/',
  'https://www.linkedin.com/in/kanishk-kumar-95349127b/',
  'https://www.linkedin.com/in/sakshi-mhasde-b18146286/',
  'https://www.linkedin.com/in/avyaanverma/'
];

// Array to store scraped profile data
const scrapedData = [];

// Main asynchronous function to run the scraping process
(async () => {
  // Array of user-agent strings for mimicking different browsers
  const userAgents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/91.0'
  ];

  // Launch a persistent browser context with a random user-agent
  const context = await chromium.launchPersistentContext('', {
    headless: false, // Open the browser in a visible window
    userAgent: userAgents[Math.floor(Math.random() * userAgents.length)], // Randomly select a user-agent
    viewport: { width: 1280, height: 800 } // Set the browser viewport size
  });

  // Create a new page in the browser context
  const page = await context.newPage();

  // Navigate to LinkedIn login page and wait for manual login
  await page.goto('https://www.linkedin.com/login');
  console.log("Please log in manually."); // Prompt user to log in manually
  await page.waitForTimeout(60000); // Wait for up to 60 seconds for the user to log in

  // Loop through each LinkedIn profile URL in the list
  for (const profileUrl of profilesToScrape) {
    console.log(`Scraping profile: ${profileUrl}`); // Log the current profile being scraped
    await page.goto(profileUrl); // Navigate to the profile URL

    // Mimic human scrolling action
    await page.evaluate(() => window.scrollBy(0, window.innerHeight / 2)); // Scroll halfway down the page
    await page.waitForTimeout(Math.random() * 5000 + 3000); // Wait for a random time between 3-8 seconds

    // Scrape data from the profile page
    const profileData = await page.evaluate(() => {
      const name = document.querySelector('.text-heading-xlarge')?.innerText || 'N/A'; // Get profile name
      const headline = document.querySelector('.text-body-medium')?.innerText || 'N/A'; // Get profile headline
      const location = document.querySelector('.text-body-small.inline')?.innerText || 'N/A'; // Get location
      
      // Try to locate the About section using various selectors
      const aboutSection = document.querySelector('.pv-about-section') ||
                           document.querySelector('section:has(h2[aria-label="About"]) p') ||
                           document.querySelector('section:has(h2) > p');
      const about = aboutSection?.innerText || 'N/A'; // Get About section text

      // Return collected data as an object
      return { name, headline, location, about };
    });

    console.log(`Data for profile:`, profileData); // Log the scraped data
    scrapedData.push(profileData); // Add the profile data to the array

    // Mimic human interactions to avoid detection
    await page.mouse.move(200 + Math.random() * 500, 200 + Math.random() * 500); // Random mouse movement
    await page.click('body'); // Random click on the page
    await page.waitForTimeout(Math.random() * 5000 + 5000); // Wait a random time (5-10 seconds) between profiles
  }

  // Define the file path for the CSV file to save the scraped data
  const csvFilePath = path.join(__dirname, 'scraped_profiles.csv');
  
  // Create CSV headers
  const csvHeader = 'Name,Headline,Location,About\n';
  
  // Format scraped data as CSV rows
  const csvRows = scrapedData
    .map(data => `${data.name},${data.headline},${data.location},${data.about.replace(/\n/g, ' ')}`)
    .join('\n');
  
  // Write the CSV headers and data rows to a file
  fs.writeFileSync(csvFilePath, csvHeader + csvRows);
  console.log(`Scraped data saved to ${csvFilePath}`); // Notify that data has been saved

  // Close the browser context
  await context.close();
})();




/*description-How It Works:
Setup: The code imports necessary modules (playwright, fs, and path) and defines an array of LinkedIn profile URLs to scrape.

Browser Launch and Login: A persistent browser session is launched with randomized user-agents and viewport dimensions to simulate different browser environments. The user is prompted to log in manually, with a 60-second delay to allow login completion.

Profile Scraping: For each profile:

It navigates to the profile URL and performs human-like scrolling.
It extracts basic information: name, headline, location, and About section (using multiple selector checks to locate the About section).
Data Storage: The extracted data is formatted as CSV content and saved to a file named scraped_profiles.csv.

Anti-Bot Techniques: The script mimics human interactions by adding randomized mouse movements, clicks, and delays between profile visits to evade LinkedIn's bot-detection mechanisms.

Completion: After all profiles are scraped, the browser session closes, and the data is available in the CSV file.*/
