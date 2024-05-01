from celery import shared_task
import flask_excel as excel
from .mail_service import send_message
from .models import db,User, Role,UserLogin,Track,Album
from jinja2 import Template
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt
import os

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet



@shared_task(ignore_result=True)
def daily_reminder(to, subject):
    today = datetime.now().date()
    users = User.query.filter(User.roles.any(Role.name != 'admin')).all()
    for user in users:
        last_login = UserLogin.query.filter_by(user_id=user.id).order_by(UserLogin.login_time.desc()).first()
        if last_login is None or last_login.login_time.date() < today:
            send_message(user.email, subject, f'Dear {user.username},<br>Please log in to our app today!')
    return "OK"

@shared_task(ignore_result=True)
def monthly_pdf_reminder():
    users = User.query.filter(User.roles.any(Role.name == 'creator')).all()
    for user in users:
        generate_pdf(user.email)
    return "OK"

import os
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet



def generate_pdf(email):
    # Perform necessary queries to get data for plotting
    user = User.query.filter_by(email=email).first()
    if not user:
        return None
    
    # Retrieve tracks added by the user
    user_tracks = Track.query.filter_by(added_by=user.id).all()
    user_albums = Album.query.filter_by(added_by=user.id).all()
    
    # 1. Highest rated songs belonging to the user (top 10)
    top_rated_songs = sorted(user_tracks, key=lambda x: x.average_rating, reverse=True)[:10]
    ratings = [song.average_rating for song in top_rated_songs]
    song_titles = [song.title for song in top_rated_songs]
    
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.barh(song_titles, ratings, color='skyblue')
    ax.set_xlabel('Average Rating')
    ax.set_ylabel('Song Title')
    ax.set_title('Top 10 Highest Rated Songs')
    ax.invert_yaxis()  # Invert y-axis to display highest rating at the top
    plt.tight_layout()
    top_rated_songs_img = io.BytesIO()
    plt.savefig(top_rated_songs_img, format='png')
    plt.close()

    # 2. Highest streamed songs belonging to the user (top 10)
    top_streamed_songs = sorted(user_tracks, key=lambda x: x.stream_count, reverse=True)[:10]
    stream_counts = [song.stream_count for song in top_streamed_songs]
    song_titles = [song.title for song in top_streamed_songs]
    
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.barh(song_titles, stream_counts, color='lightgreen')
    ax.set_xlabel('Stream Count')
    ax.set_ylabel('Song Title')
    ax.set_title('Top 10 Highest Streamed Songs')
    ax.invert_yaxis()  # Invert y-axis to display highest stream count at the top
    plt.tight_layout()
    top_streamed_songs_img = io.BytesIO()
    plt.savefig(top_streamed_songs_img, format='png')
    plt.close()

    # 3. List of all genres of the songs created by the user with genre-wise streams
    genre_streams = {}
    for track in user_tracks:
        genre_streams[track.genre] = genre_streams.get(track.genre, 0) + track.stream_count

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(genre_streams.keys(), genre_streams.values(), color='salmon')
    ax.set_xlabel('Genre')
    ax.set_ylabel('Total Streams')
    ax.set_title('Genre-wise Streams of Songs Created by User')
    ax.tick_params(axis='x', rotation=45)
    plt.tight_layout()
    genre_wise_streams_img = io.BytesIO()
    plt.savefig(genre_wise_streams_img, format='png')
    plt.close()

    # 4. Highest streamed albums (top 10)
    top_streamed_albums = sorted(user_albums, key=lambda x: sum([track.stream_count for track in x.tracks]), reverse=True)[:10]
    album_titles = [album.title for album in top_streamed_albums]
    album_streams = [sum([track.stream_count for track in album.tracks]) for album in top_streamed_albums]

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(album_titles, album_streams, color='gold')
    ax.set_xlabel('Album Title')
    ax.set_ylabel('Total Streams')
    ax.set_title('Top 10 Highest Streamed Albums')
    ax.tick_params(axis='x', rotation=45)
    plt.tight_layout()
    top_streamed_albums_img = io.BytesIO()
    plt.savefig(top_streamed_albums_img, format='png')
    plt.close()

    # Generate PDF file
    pdf_filename = f'{user.email}_monthly_report.pdf'
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter)
    pdf_content = []

    # Add top rated songs image
    top_rated_songs_img.seek(0)
    pdf_content.append(Image(top_rated_songs_img))

    # Add top streamed songs image
    top_streamed_songs_img.seek(0)
    pdf_content.append(Image(top_streamed_songs_img))

    # Add genre-wise streams image
    genre_wise_streams_img.seek(0)
    pdf_content.append(Image(genre_wise_streams_img))

    # Add top streamed albums image
    top_streamed_albums_img.seek(0)
    pdf_content.append(Image(top_streamed_albums_img))

    doc.build(pdf_content)

    # Send the PDF file via email using MailHog
    send_message(user.email, "Monthly Report", f'Dear {user.username},<br>Please find your monthly report attached.', pdf_filename)

    return pdf_filename