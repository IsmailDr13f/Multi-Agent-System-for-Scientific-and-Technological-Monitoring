from typing import List, Optional
from pydantic import BaseModel, Field


# 1. Academic Paper Researcher Model
class AcademicPaper(BaseModel):
    title: str = Field(..., description="Title of the academic paper.")
    authors: List[str] = Field(..., description="List of authors of the paper.")
    publication_date: str = Field(..., description="Publication date of the paper.")
    abstract: str = Field(..., description="Abstract of the paper.")
    key_findings: List[str] = Field(..., description="Key findings or contributions of the paper.")
    relevance: str = Field(..., description="Why this paper is relevant to the query.")
    source: str = Field(..., description="Source of the paper (arxiv, journal, etc.).")

class AcademicResearchResponse(BaseModel):
    query_summary: str = Field(..., description="A summary of the research query.")
    papers: List[AcademicPaper] = Field(..., description="List of relevant academic papers.")
    synthesis: str = Field(..., description="A synthesis of the findings across papers.")
    future_directions: str = Field(..., description="Potential future research directions based on findings.")

# 2. Search Engine Agent Model
class SearchResult(BaseModel):
    title: str = Field(..., description="Title of the search result.")
    url: str = Field(..., description="URL of the search result.")
    summary: str = Field(..., description="Brief summary of the content.")
    post_date: Optional[str] = Field(None, description="Date when the content was posted.")
    #relevance_score: int = Field(..., description="Relevance score from 1-10.")

class SearchResponse(BaseModel):
    query_interpretation: str = Field(..., description="How the search engine interpreted the query.")
    results: List[SearchResult] = Field(..., description="List of search results.")
    top_insights: List[str] = Field(..., description="Key insights extracted from the search results.")
    #suggested_follow_up_queries: List[str] = Field(..., description="Suggested follow-up queries.")


# 3. Video Agent Model
class VideoContent(BaseModel):
    title: str = Field(..., description="Title of the video.")
    channel: str = Field(..., description="Channel or creator of the video.")
    duration: str = Field(..., description="Duration of the video.")
    upload_date: Optional[str] = Field(None, description="Upload date of the video.")
    key_points: List[str] = Field(..., description="Key points discussed in the video.")
    summary: str = Field(..., description="Comprehensive summary of the video content.")
    timestamps: Optional[dict] = Field(None, description="Important timestamps and their descriptions.")

class VideoResponse(BaseModel):
    video_info: VideoContent = Field(..., description="Information about the video.")
    related_videos: Optional[List[str]] = Field(None, description="Related videos on the topic.")
    additional_resources: Optional[List[str]] = Field(None, description="Additional resources for further exploration.")


# 4. Social Media Researcher Model
class SocialMediaTrend(BaseModel):
    topic: str = Field(..., description="Topic of the trend.")
    key_influencers: List[str] = Field(..., description="Key people discussing this topic.")
    popularity_level: str = Field(..., description="How popular the trend is (viral, rising, stable).")
    key_discussions: List[str] = Field(..., description="Main points being discussed.")
    post_date: Optional[str] = Field(None, description="Date when the trend started.")
    

class SocialMediaResearchResponse(BaseModel):
    current_trends: List[SocialMediaTrend] = Field(..., description="Current trending topics on social media.")