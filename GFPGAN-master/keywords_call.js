const axios = require('axios');
const fs = require('fs');

async function uploadImageAndGetKeywords(imagePath) {
    try {
        // Step 1: Upload the image and get the URL
        const imageData = fs.readFileSync(imagePath); // Read image from the file system
        const uploadResponse = await axios.post('https://your-image-upload-api.com/upload', {
            image: imageData.toString('base64'), // Convert image to base64 string
        });

        const imageUrl = uploadResponse.data.url; // Assuming the response contains the image URL
        console.log(`Image uploaded successfully. URL: ${imageUrl}`);

        // Step 2: Use the URL to get keywords
        const keywordsResponse = await axios.post('https://your-keyword-extraction-api.com/getKeywords', {
            url: imageUrl,
        });

        const keywords = keywordsResponse.data.keywords; // Assuming the response contains a 'keywords' array
        console.log('Extracted Keywords:', keywords);

        return keywords;
    } catch (error) {
        console.error('Error:', error.message);
    }
}

// Replace 'path/to/your/image.jpg' with the actual path to your image
uploadImageAndGetKeywords('path/to/your/image.jpg');
