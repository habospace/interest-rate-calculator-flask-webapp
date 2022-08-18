from flask.views import MethodView


class Loan(MethodView):

    def get(self, loan_id):
        if loan_id is None:
            # return a list of users
            return {"loans": []}
        else:
            # expose a single user
            return {"data": []}

    def post(self):
        # create a new user
        loan_id = 0
        return loan_id

    def delete(self, loan_id):
        # delete a single user
        return loan_id

    def put(self, loan_id):
        # update a single user
        return id
