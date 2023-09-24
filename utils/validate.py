
def validate(key, value):
    error = '{} is required'.format(key)
    if value == None:
        return True, error
    if value.replace(" ","") == "":
        return True, error
    return False, "Success"

def validate_dict(data={"name":"", "email":""}):
    errors =  [validate(k,v) for k,v in data.items()]
    for status, msg in errors:
        if(status):
            return {'message': msg}
    return False

