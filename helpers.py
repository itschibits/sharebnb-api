import jwt

def get_token(username):
	return jwt.encode({username: username})
