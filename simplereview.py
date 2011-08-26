#!/usr/bin/env python

import os

from simplereview.diffparser import parse
from simplereview.domain import Review
from simplereview.repositories import SqliteReviewRepository

import web

repo = SqliteReviewRepository(os.getenv("DB_PATH", "dev.db"))
render = web.template.render(os.getenv("TEMPLATE_DIR", "templates/"), base="base")
urls = (
    "/", "list_reviews",
    "/create_review", "create_review",
    "/review/(.*)/comments_json", "comments_json",
    "/review/(.*)/add_comment", "add_comment",
    "/review/(.*)", "review",
    "/review_diff/(.*)", "review_diff",
)

class list_reviews:
    def GET(self):
        return render.list_reviews(repo.list_by_date())

class create_review:
    def POST(self):
        i = web.webapi.input()
        repo.save(Review(name=i.name))

class comments_json:
    def GET(self, review_id):
        web.header("Content-Type", "application/json")
        return repo.find_by_id(review_id).comments_json()

class add_comment:
    def POST(self, review_id):
        i = web.webapi.input()
        repo.add_comment(review_id, i.author, i.comment)
        web.seeother("/review/%s" % review_id)

class review:
    def GET(self, review_id):
        return render.review(repo.find_by_id(review_id))

class review_diff:
    def GET(self, review_id):
        web.header("Content-Type", "application/json")
        return parse(repo.find_by_id(review_id).diff).to_json()

if __name__ == "__main__":
    web.application(urls, globals()).run()