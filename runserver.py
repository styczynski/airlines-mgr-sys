#
# Python utility to launch django dev server
# along with background task processor and redis server
# (if the Redis is available)
#
#
#  Piotr Styczyński @styczynski
#  March 2018 MIT LICENSE
#
from subprocess import call, Popen

background_processor = None
channels_processor = None
redis_server = None

#channels_processor = Popen(['python', 'manage.py', 'process_tasks'])

try:
  # Run background task runner
  background_processor = Popen(['python', 'manage.py', 'process_tasks'])
except:
  background_processor = None

# Run Django devserver
call(['python', 'manage.py', 'runserver'])

try:
  background_processor.terminate()
except:
   background_processor = None