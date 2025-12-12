vectorizedb/
├── docker-compose.yml
├── .env
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models/
│   │   │   └── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── upload.py
│   │   │   └── chat.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── file_processor.py
│   │   │   ├── embeddings.py
│   │   │   └── chatbot.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── helpers.py
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── vite.config.ts
│   ├── public/
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── components/
│       │   ├── Auth/
│       │   ├── Dashboard/
│       │   ├── FileUpload/
│       │   ├── DataPreview/
│       │   └── ChatBot/
│       ├── services/
│       │   └── api.ts
│       ├── hooks/
│       └── types/
└── README.md