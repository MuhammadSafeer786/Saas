const express = require('express');
const multer = require('multer');
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
const path = require('path');

const app = express();
const port = 3000;

// Serve static files (e.g., CSS, JS) from the 'public' directory
app.use(express.static('public'));

// Set up multer for file upload
const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, 'upscaler_imgs/uploads/');
    },
    filename: function (req, file, cb) {
        cb(null, file.originalname);
    }
});

const upload = multer({ storage: storage });

// Serve the HTML form
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'upscale_client.html'));
});

// Handle file upload and processing
app.post('/upload', upload.single('image'), (req, res) => {
    if (!req.file) {
        return res.status(400).json({ error: 'No file uploaded' });
    }

    const imagePath = path.join(__dirname, 'upscaler_imgs', 'uploads', req.file.filename);

    // Send image to the specified API
    const form = new FormData();
    form.append('image', fs.createReadStream(imagePath));

    axios.post('http://localhost:3001/enhance', form, {
        headers: {
            ...form.getHeaders()
        },
        responseType: 'arraybuffer'
    }).then(response => {
        const outputFilePath = path.join(__dirname, 'Upscaler_imgs', 'out', 'out.png');
        fs.writeFileSync(outputFilePath, response.data);

        // Send back the download URL
        res.json({
            message: 'Image processed successfully',
            downloadUrl: `/download/${path.basename(outputFilePath)}`
        });
    }).catch(error => {
        res.status(500).json({ error: 'Error processing image: ' + error.message });
    });
});

// Serve the processed image file
app.get('/download/:filename', (req, res) => {
    const file = path.join(__dirname, 'Upscaler_imgs','out', req.params.filename);
    if (fs.existsSync(file)) {
        res.sendFile(file);
    } else {
        res.status(404).send('File not found');
    }
});

// Start the server
app.listen(port, () => {
    console.log(`Server running on http://localhost:${port}`);
});
