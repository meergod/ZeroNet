import gevent, time

class Noparallel(object): # Only allow function running once in same time
	def __init__(self,blocking=True):
		self.threads = {}
		self.blocking = blocking # Blocking: Acts like normal function else thread returned


	def __call__(self, func):
		def wrapper(*args, **kwargs):
			key = (func, tuple(args), tuple(kwargs)) # Unique key for function including parameters
			if key in self.threads: # Thread already running (if using blocking mode)
				thread = self.threads[key]
				if self.blocking:
					thread.join() # Blocking until its finished
					return thread.value # Return the value
				else: # No blocking
					if thread.ready(): # Its finished, create a new
						thread = gevent.spawn(func, *args, **kwargs)
						self.threads[key] = thread
						return thread
					else: # Still running
						return thread
			else: # Thread not running
				thread = gevent.spawn(func, *args, **kwargs) # Spawning new thread
				self.threads[key] = thread
				if self.blocking: # Wait for finish
					thread.join()
					ret = thread.value
					if key in self.threads: del(self.threads[key]) # Allowing it to run again
					return ret
				else: # No blocking just return the thread
					return thread
		wrapper.func_name = func.func_name
		
		return wrapper

class Test():
	@Noparallel()
	def count(self):
		for i in range(5):
			print self, i
			time.sleep(1)
		return "%s return:%s" % (self, i)


class TestNoblock():
	@Noparallel(blocking=False)
	def count(self):
		for i in range(5):
			print self, i
			time.sleep(1)
		return "%s return:%s" % (self, i)


def testBlocking():
	test = Test()
	test2 = Test()
	print "Counting..."
	print "Creating class1/thread1"
	thread1 = gevent.spawn(test.count)
	print "Creating class1/thread2 (ignored)"
	thread2 = gevent.spawn(test.count)
	print "Creating class2/thread3"
	thread3 = gevent.spawn(test2.count)

	print "Joining class1/thread1"
	thread1.join()
	print "Joining class1/thread2"
	thread2.join()
	print "Joining class2/thread3"
	thread3.join()

	print "Creating class1/thread4 (its finished, allowed again)"
	thread4 = gevent.spawn(test.count)
	print "Joining thread4"
	thread4.join()

	print thread1.value, thread2.value, thread3.value, thread4.value
	print "Done."

def testNoblocking():
	test = TestNoblock()
	test2 = TestNoblock()
	print "Creating class1/thread1"
	thread1 = test.count()
	print "Creating class1/thread2 (ignored)"
	thread2 = test.count()
	print "Creating class2/thread3"
	thread3 = test2.count()
	print "Joining class1/thread1"
	thread1.join()
	print "Joining class1/thread2"
	thread2.join()
	print "Joining class2/thread3"
	thread3.join()

	print "Creating class1/thread4 (its finished, allowed again)"
	thread4 = test.count()
	print "Joining thread4"
	thread4.join()


	print thread1.value, thread2.value, thread3.value, thread4.value
	print "Done."

if __name__ == "__main__":
	from gevent import monkey
	monkey.patch_all()

	print "Testing blocking mode..."
	testBlocking()
	print "Testing noblocking mode..."
	testNoblocking()
