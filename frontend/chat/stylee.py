style="""
<style>
.article-card {
    background: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 12px;
    padding: 25px;
    margin-bottom: 50px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    color: #333;
}

.card-content {
    display: flex;
    align-items: flex-start;
    gap: 30px;
}

.card-info {
    flex: 1;
}

.card-title {
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 15px;
    line-height: 1.3;
    color: #2c3e50;
}

.card-meta {
    display: flex;
    gap: 15px;
    margin-bottom: 20px;
    font-size: 14px;
}

.card-source {
    background: #e3f2fd;
    color: #1976d2;
    padding: 6px 14px;
    border-radius: 20px;
    font-weight: 500;
}

.card-date {
    background: #f3e5f5;
    color: #7b1fa2;
    padding: 6px 14px;
    border-radius: 20px;
    font-weight: 500;
}

.card-topic {
    background: #e8f5e8;
    color: #388e3c;
    padding: 6px 14px;
    border-radius: 20px;
    font-weight: 600;
}

.card-summary {
    font-size: 16px;
    line-height: 1.6;
    margin-bottom: 20px;
    color: #555;
}

.card-image {
    width: 300px;
    height: 220px;
    border-radius: 12px;
    object-fit: cover;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.card-link-button {
    display: inline-block;
    background: #007bff;
    color: white;
    text-decoration: none;
    padding: 12px 24px;
    border-radius: 8px;
    font-weight: 600;
    font-size: 14px;
    transition: all 0.3s ease;
    border: none;
    cursor: pointer;
}

.card-link-button:hover {
    background: #0056b3;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
    text-decoration: none;
    color: white;
}

.chat-container {
    background: #ffffff;
    border-radius: 10px;
    padding: 20px;
    margin-top: 30px;
}

.user-message {
    background: #007bff;
    color: white;
    padding: 12px 16px;
    border-radius: 18px 18px 4px 18px;
    margin: 8px 0;
    margin-left: 20%;
    word-wrap: break-word;
}

.assistant-message {
    background: #f8f9fa;
    color: #333;
    padding: 12px 16px;
    border-radius: 18px 18px 18px 4px;
    margin: 8px 0;
    margin-right: 20%;
    word-wrap: break-word;
    border: 1px solid #e9ecef;
}

@media (max-width: 768px) {
    .card-content {
        flex-direction: column;
    }
    .card-image {
        width: 100%;
        height: 250px;
    }
    .user-message, .assistant-message {
        margin-left: 0;
        margin-right: 0;
    }
}
</style>
"""