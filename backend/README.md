Fake-News-Detection/
│
├── 📂 backend/
│   ├── 📂 model/
│   │   ├── fake_news_bert_model/        # Trained BERT model
│   │   │   ├── config.json
│   │   │   ├── pytorch_model.bin
│   │   │   └── tokenizer files
│   │   └── model_info.json              # Model metadata
│   │
│   ├── 📂 api/
│   │   ├── __init__.py
│   │   ├── main.py                      # FastAPI application
│   │   ├── prediction.py                # Prediction logic
│   │   └── verification.py              # Source verification
│   │
│   ├── 📂 utils/
│   │   ├── __init__.py
│   │   ├── text_processing.py           # Text cleaning functions
│   │   ├── file_extractor.py            # PDF/DOC/Image extraction
│   │   └── config.py                    # Configuration settings
│   │
│   ├── requirements.txt                 # Python dependencies
│   ├── .env                            # Environment variables
│   └── README.md                       