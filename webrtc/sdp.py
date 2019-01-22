import clock

class SessionDescription:

    def __init__(self):
        self.version = 0
        """
        RFC4566 5-2
        o=<origin>
        <username> is '-'
        <sess-id>, <sess-version> is recommended NTP format timestamp
        """
        self.origin = None
        """
        RFC4566 5-3
        s=<sssion name>
        """
        self.session_name = '-'
        """
        RFC4566 5-4
        i=<session information>
        """
        self.session_information = None
        """
        RFC4566 5-5
        u=<uri>
        """
        self.uri = None
        """
        RFC4566 5-6
        e=<email-address>
        p=<phone-number>
        """
        self.email_address = None
        self.phone_number = None
        """
        RFC4566 5-7
        c=<connection data>
         =<nettype> <addrtype> <connection-address>
        """
        self.connection_data = None
        """
        RFC4566 5-8
        b=<bandwidth>
         =<bwtype>:<bandwidth>
        """
        self.bandwidth = None
        """
        RFC6455 5-9
        t=<timing>
         =<start-time> <stop-time>
        if both fields is set to zero, the session is regarded as permanent
        """
        self.timing = '0 0'
        """
        RFC4566 5-10
        r=<repeat time>
         =<repeat interval> <active duration> <offsets from start-time>
        """
        self.repeat_time = None
        """
        RFC4566 5-11
        z=<adjustment time> <offset> <adjustment time> <offset> ....
        """
        self.time_zone = None
        """
        RFC4566 5-12
        k=<method>
        k=<method>:<encryption key>
        """
        self.encryption_key = None
        """
        RFC4566 5-13
        a=<attribute>
        a=<attribute>:<value>
        """
        self.attributes = []
        """
        RFC4566 5-14
        m=<media> <port> <proto> <fmt> ....
        """
        self.media_description = []

class PeerConnection:

    def __init__(self):
        pass

    def createOffer(self):

        ntp_second = clock.current_ntp_time() >> 32
        description = SessionDescription()
        description.origin = '- {} {} IN IP4 0.0.0.0'.format(ntp_second, ntp_second)
