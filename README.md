# Tom City Edition - Telugu E-Paper Platform

A modern, mobile-friendly digital newspaper platform for Tom City Edition, built with GitHub Pages automation.

## 🌟 Features

- **Daily E-Paper**: Automated PDF to image conversion
- **Mobile Optimized**: Responsive design for all devices
- **Page Navigation**: Easy browsing with previous/next controls
- **Edition Selector**: Access past editions by date
- **Clipper Tool**: Crop and share news snippets
- **PDF Download**: Download full edition as PDF
- **GitHub Actions**: Automated publishing workflow

## 🛠️ Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript
- **Automation**: GitHub Actions
- **PDF Processing**: Python (Pillow, pdftoppm)
- **Image Cropping**: Cropper.js
- **Hosting**: GitHub Pages

## 📁 Project Structure

```
tom-city-edition/
├── .github/
│   └── workflows/
│       └── daily-paper.yml       # GitHub Actions automation
├── assets/
│   ├── logo.png                  # Website logo
│   ├── favicon.png               # Browser icon
│   ├── latest-cover.jpg          # Social media preview
│   └── page-flip-4.mp3           # Page turn sound
├── papers/
│   └── [date-folders]/           # Each edition stored by date
│       ├── 1.png                 # Page images
│       ├── 2.png
│       └── full.pdf              # Complete PDF
├── scripts/
│   └── process_pdf.py            # PDF processing script
├── uploads/
│   └── .gitkeep                  # Placeholder for PDF uploads
├── index.html                    # Main website
├── style.css                     # Styling
├── app.js                        # Functionality
└── CNAME                         # Custom domain config

```

## 🚀 How It Works

1. **Upload PDF**: Place PDF file in `uploads/` folder (format: `DD-MM-YYYY.pdf`)
2. **Automatic Processing**: GitHub Actions triggers on upload
3. **Conversion**: PDF converts to PNG images automatically
4. **Website Update**: New edition appears on website instantly

## 📝 Publishing a New Edition

1. Create PDF file named with date: `08-02-2026.pdf`
2. Upload to `uploads/` folder
3. Commit and push to GitHub
4. GitHub Actions will automatically:
   - Convert PDF to images
   - Create edition folder
   - Update website
   - Generate social media preview

## 🎨 Customization

- **Theme Color**: `#2f96f0` (defined in `style.css`)
- **Logo**: Replace `assets/logo.png`
- **Favicon**: Replace `assets/favicon.png`
- **Social Links**: Update in `index.html`

## 👨‍💻 Developer

**Built by:** html-ramu  
**GitHub:** [@html-ramu](https://github.com/html-ramu)  
**Client:** Tom City Edition  
**Domain:** tom-city-edition.in

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues or questions, contact the developer through GitHub.

---

**© 2026 Tom City Edition | All Rights Reserved**
