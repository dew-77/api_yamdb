from django.core.management.base import BaseCommand, CommandError
from core.models import Category, Genre, Title, User, Review, Comment
import csv
import os


class Command(BaseCommand):
    help = ""

    def handle(self, *args, **options):
        os.chdir("static/data")
        with open("users.csv", encoding="utf8") as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            for row in reader:
                User.objects.get_or_create(
                    id=row[0],
                    username=row[1],
                    email=row[2],
                    role=row[3],
                )
        with open("category.csv", encoding="utf8") as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            for row in reader:
                Category.objects.get_or_create(
                    id=row[0],
                    name=row[1],
                    slug=row[2],
                )
        with open("genre.csv", encoding="utf8") as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            for row in reader:
                Genre.objects.get_or_create(
                    id=row[0],
                    name=row[1],
                    slug=row[2],
                )
        with open("titles.csv", encoding="utf8") as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            for row in reader:
                Title.objects.get_or_create(
                    id=row[0],
                    name=row[1],
                    year=row[2],
                    category=Category.objects.get(id=row[3]),
                )
        with open("review.csv", encoding="utf8") as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            for row in reader:
                Review.objects.get_or_create(
                    id=row[0],
                    title=Title.objects.get(id=row[1]),
                    text=row[2],
                    author=User.objects.get(id=row[3]),
                    score=row[4],
                    pub_date=row[5],
                )
        with open("comments.csv", encoding="utf8") as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            for row in reader:
                Comment.objects.get_or_create(
                    id=row[0],
                    review=Review.objects.get(id=row[1]),
                    text=row[2],
                    author=User.objects.get(id=row[3]),
                    pub_date=row[4],
                )
