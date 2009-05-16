"""Unit test for zui/messager.py."""

import sys,os
sys.path.append(os.path.join(sys.path[0],'../zui/'))
from messager import messager, Receiver

import unittest

class Logger(Receiver):
    """An object that maintains a log, in self.log, of the order in which its
    methods foo and bar are called and the arguments that are passed to them.
    Each item in the list is a 2-tuple: the method that was called, and a tuple
    of the arguments that were passed to it."""
 
    def __init__(self):

        # FIXME: log should be a class variable that all instances log to. 
        self.log = []
 
    def foo(self,*args):

        self.log.append((self.foo,args))
 
    def bar(self,*args):
 
        self.log.append((self.bar,args))

class MessagerTest(unittest.TestCase):

    def setUp(self):
    
        self.logger = Logger()
        
    def tearDown(self):
        pass

    # Accepting and sending messages.
    def testMultipleAccept(self):
        """foo and bar are subscribed to message a, when a is sent both foo and
        bar should be called."""

        self.logger.accept('a',self.logger.foo)
        self.logger.accept('a',self.logger.bar)

        messager.send('a')
        # Two methods were called.
        self.assertEqual(len(self.logger.log),2)
        # foo was called once.
        count = self.logger.log.count((self.logger.foo,()))
        self.assertEqual(count,1)
        # bar was called once.
        count = self.logger.log.count((self.logger.bar,()))
        self.assertEqual(count,1)
        
    def testAcceptOnce(self):
        """foo is subscribed to message b once only, bar is subscribed to it
        permanently. If b is sent twice, foo and bar should be called the first
        time, only bar should be called the second time."""

        self.logger.acceptOnce('b',self.logger.foo)
        self.logger.accept('b',self.logger.bar)
        
        messager.send('b')
        # foo should have been called once.
        count = self.logger.log.count((self.logger.foo,()))
        self.assertEqual(count,1)
        # bar should have been called once.
        count = self.logger.log.count((self.logger.bar,()))
        self.assertEqual(count,1)
        messager.send('b')
        # foo should still have been called only once.
        count = self.logger.log.count(( self.logger.foo,()))
        self.assertEqual(count,1)
        # bar should now have been called twice.
        count = self.logger.log.count((self.logger.bar,()))
        self.assertEqual(count,2)

    # Ignoring messages.
    def testIgnore(self):
        """foo and bar are subscribed to c, after ignore(c,foo) only bar should
        be called when c is sent."""

        self.logger.accept('c',self.logger.foo)
        self.logger.accept('c',self.logger.bar)
        self.logger.ignore('c',self.logger.foo)
        messager.send('c')
        # Only one method should have been called.
        self.assertEqual(len(self.logger.log),1)
        # bar should have been called once.
        count = self.logger.log.count((self.logger.bar,()))
        self.assertEqual(count,1)

    def testIgnoreMessage(self):
        """foo and bar are subscribed to c, after ignore(c) neither foo nor bar
        should be called."""

        self.logger.accept('c',self.logger.foo)
        self.logger.accept('c',self.logger.bar)
        self.logger.ignore('c')
        messager.send('c')
        # No methods should have been called.
        self.assertEqual(self.logger.log,[])
      
    def testIgnoreAll(self):
        """After a Receiver object calls ignoreAll() no methods of this object
        should be called when any message is sent, but methods of other objects 
        should continue to be called."""

        self.logger.accept('d',self.logger.foo)
        self.logger.accept('e',self.logger.bar)
        second_logger = Logger()
        second_logger.accept('d',second_logger.foo)
        second_logger.accept('e',second_logger.bar)

        self.logger.ignoreAll()
        messager.send('d')
        messager.send('e')
        # No methods of logger should have been called.
        self.assertEqual(self.logger.log,[])
        # Two methods should have been called on second_logger.
        self.assertEqual(len(second_logger.log),2)
        # foo should have been called once.
        count = second_logger.log.count((second_logger.foo,()))
        self.assertEqual(count,1)
        # bar should have been called once.
        count = second_logger.log.count((second_logger.bar,()))
        self.assertEqual(count,1)

    # Clear.
    def testClear(self):
        """After clear has been called, sending a message should not result in
        any functions being called."""
        
        messager.clear()
        messager.send('a')
        messager.send('b')
        messager.send('c')
        # No methods should have been called.
        self.assertEqual(self.logger.log,[])

    # Sending with arguments.    
    def testSendWithTwoArguments(self):
        """If accept is called with an argument and then send is called with an
        argument (and the same message name) the function subscribed via accept
        should be called with accept's argument followed by send's argument."""
        
        self.logger.accept('f',self.logger.foo,'accepter arg')
        messager.send('f','sender arg')
        # One method should have been called.
        self.assertEqual(len(self.logger.log),1)
        # foo should have been called with the two arguments in the right order.
        count = self.logger.log.count((self.logger.foo,('accepter arg','sender arg')))        
        self.assertEqual(count,1)
        
    def testSendWithNoAccepterArgument(self):
        """If no argument is given to the accept method, but an argument is
        given to the send method, then the subscribed function(s) should be
        called with the send argument only."""
        
        self.logger.accept('foo',self.logger.foo)
        messager.send('foo','sender arg')
        # One method should have been called.
        self.assertEqual(len(self.logger.log),1)
        # foo should have been called with the right argument.
        count = self.logger.log.count((self.logger.foo,('sender arg',)))        
        self.assertEqual(count,1)

    def testSendWithNoSenderArgument(self):
        """If no argument is given to the send method, but an argument is given
        to the accept method, then the subscribed function(s) should be called
         with the accept argument only."""
        
        self.logger.accept('foo',self.logger.foo,'accepter arg')
        messager.send('foo')
        # One method should have been called.
        self.assertEqual(len(self.logger.log),1)
        # foo should have been called with the right argument.
        count = self.logger.log.count((self.logger.foo,('accepter arg',)))        
        self.assertEqual(count,1)
        
if __name__ == '__main__':
    unittest.main()        