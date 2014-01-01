import inspect
import time

def WriteTestLog(message):
    """
    Print a Log message for tests. 
    """
    # The message format is: [time] => TEST => [file] => [message]
    frame = inspect.stack()[1]
    file_name = inspect.getsourcefile(frame[0])
    message = '[%s] => TEST => %s => %s' % \
        (time.strftime('%I:%M:%S'), file_name, message)
    try:
        print(message)
        #open(os.path.join('d:\\', 'subit.log'), 'a').write(message + '\r\n')
    except:
        try:
            print(message.encode('utf-8', 'ignore').decode('ascii', 'ignore'))
        except: pass