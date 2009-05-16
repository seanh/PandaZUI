"""
messager.py -- a simple message-passing pattern for one-many or many-many 
               dependencies. Useful for event notifications, for example.

To send a message use the singleton messager instance:

    from messager import messager

    messager.send('message name',argument)

You can pass a single argument with a message, and this argument can be anything
you like. For example, event objects that simply hold a number of attributes can
be constrcuted and passed as arguments with messages.
    
Messager maintains a mapping of message names to lists of functions (and their
arguments). When a message is sent, all of the functions subscribed to that
message are called and passed the argument given when the function was
subscribed followed by argument given when the message was sent. To subscribe a
function you must subclass Receiver and call the accept(...)  or acceptOnce(...) 
methods:

    self.accept('message name',function,argument)

    self.acceptOnce('message name',function,argument)

You don't need to call Receiver.__init__() when you subclass Receiver, it has no
__init__. Receiver works by maintaining a list of the message subscriptions you
have made.

It is up to you to make sure that functions that accept messages take the right
number of arguments, 0, 1 or 2 depending on whether the accept(...) and
send(...) methods were called with an argument or not.

To unsubscribe a function from a message name use ignore:

    # Unsubscribe a particular function from a particular message name.
    self.ignore('message name',function)

    # Unsubscribe all functions that this object has subscribed to a particular 
    # message name.
    self.ignore('message name')

    # Unsubscribe all functions that this object has subscribed to any message
    # name.
    self.ignoreAll()

You can unsubscribe all functions from all Receiver objects with:

    messager.clear()
        
If you do `messager.verbose = True` the messager will print whenever it
receives a message or subscription, and if you do `print messager` the messager
will print out a list of all the registered message names and their subscribers.

One last thing to be aware of is that messager keeps references to (functions
of) all objects that subscribe to accept messages. For an object to be deleted
it must unsubscribe all of its functions from all messages (the ignoreAll()
method will do this).

"""

class Messager:
    """Singleton messager object."""
   
    def __init__(self):
        """Initialise the dictionary mapping message names to lists of receiver 
        functions."""

        self.receivers = {}
        self.one_time_receivers = {}
        self.verbose = False

    def send(self,name,sender_arg='no arg'):
        """Send a message with the given name and the given argument. All
        functions registered as receivers of this message name will be
        called."""
        
        if self.verbose:
            print 'Sending message',name
        
        if self.receivers.has_key(name):
            for receiver in self.receivers[name]:
                args = []
                if receiver['arg'] != 'no arg':
                    args.append(receiver['arg'])
                if sender_arg != 'no arg':
                    args.append(sender_arg)
                receiver['function'](*args)
                if self.verbose:
                    print '   received by',receiver['function']
        
        if self.one_time_receivers.has_key(name):
            for receiver in self.one_time_receivers[name]:
                args = []
                if receiver['arg'] != 'no arg':
                    args.append(receiver['arg'])
                if sender_arg != 'no arg':
                    args.append(sender_arg)
                receiver['function'](*args)
                if self.verbose:
                    print '   received by',receiver['function']
            del self.one_time_receivers[name]
    
    def _accept(self,name,function,arg='no arg'):
        """Register with the messager to receive messages with the given name,
        messager will call the given function to notify of a message. The arg
        object given to accept will be passed to the given function first,
        followed by the arg object given to send by the sender object."""

        if not self.receivers.has_key(name):
            self.receivers[name] = []
        self.receivers[name].append({'function':function,'arg':arg})

        if self.verbose:
            print '',function,'subscribed to event',name,'with arg',arg
        
    def _acceptOnce(self,name,function,arg=None):
        """Register to receive the next instance only of a message with the
        given name."""

        if not self.one_time_receivers.has_key(name):
            self.one_time_receivers[name] = []
        self.one_time_receivers[name].append({'function':function,'arg':arg})

        if self.verbose:
            print '',function,'subscribed to event',name,'with arg',arg,'once only'
        
    def _ignore(self,name,function):
        """Unregister the given function from the given message name."""

        if self.receivers.has_key(name):        
            # FIXME: Could use a fancy list comprehension here.
            temp = []
            for receiver in self.receivers[name]:
                if receiver['function'] != function:
                    temp.append(receiver)            
            self.receivers[name] = temp

        if self.one_time_receivers.has_key(name):        
            temp = []
            for receiver in self.one_time_receivers[name]:
                if receiver['function'] != function:
                    temp.append(receiver)            
            self.one_time_receivers[name] = temp

        if self.verbose:
            print '',function,'unsubscribed from',name             
    
    def clear(self):
        """Clear all subscriptions with the messager."""
        
        self.receivers = {}
        self.one_time_receivers = {}
        
    def __str__(self):
        """Return a string showing which functions are registered with 
        which event names, useful for debugging."""
        
        string = 'Receivers:\n'
        string += self.receivers.__str__() + '\n'
        string += 'One time receivers:\n'
        string += self.one_time_receivers.__str__()
        return string

# Create the single instance of Messager.
messager = Messager()

class Receiver:
    """A class to inherit if you want to register with the messager to receive
    messages. You don't have to inherit this to register for messages, you can
    just call messager directly, but this class maintains a list of your message
    subscriptions and provides a handy ignoreAll() method, and an enhanced
    ignore(...) method."""
    
    def accept(self,name,function,arg='no arg'):
        
        # We initialise subscriptions when we first need it, to avoid having an
        # __init__ method that subclasses would need to call.
        if not hasattr(self,'subscriptions'):
            self.subscriptions = []    
        
        messager._accept(name,function,arg)
        self.subscriptions.append((name,function))
        
    def acceptOnce(self,name,function,arg='no arg'):

        if not hasattr(self,'subscriptions'):
            self.subscriptions = []    

        messager._acceptOnce(name,function,arg)
        self.subscriptions.append((name,function))
        
    def ignore(self,*args):

        if not hasattr(self,'subscriptions'):
            return

        if len(args) == 1:
            name = args[0]
            function = None
        elif len(args) == 2:
            name,function = args
        else:
            raise Exception('Wrong number of arguments to Receiver.ignore')

        if function is None:
            # Remove all of this object's function subscriptions to the given
            # message name.
            temp = []
            for subscription in self.subscriptions:
                n,f = subscription
                if n == name:
                    messager._ignore(n,f)
                else:
                    temp.append(subscription)
            self.subscriptions = temp
        else:
            # Remove the single subscription (name,function)
            messager._ignore(name,function)        
            self.subscriptions.remove((name,function))
        
    def ignoreAll(self):

        if not hasattr(self,'subscriptions'):
            return

        for subscription in self.subscriptions:
            messager._ignore(*subscription)
        self.subscriptions = []                 