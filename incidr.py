#!/usr/bin/env python

'''
Shows an IP or IPs, optionally masked, in various formats.

Example:
$ incidr 1.2.3.4/24
1.2.3.4/24 :
==========
      1.  2.  3.  4  <=>  00000001 00000010 00000011 00000100  <=>  01020304  <=>  0016909060
 &  255.255.255.  0  <=>  11111111 11111111 11111111 00000000  <=>  ffffff00  <=>  4294967040
 =    1.  2.  3.  0  <=>  00000001 00000010 00000011 00000000  <=>  01020300  <=>  0016909056
'''

import re
import socket
import struct

class Net:
    '''
    A Net is just an IP address (only v4 right now), potentially with a netmask
    applied.
    '''
    all_formats = [ 'quad', 'bin', 'dec', 'hex' ]

    def __init__(self, net, show_quad=True, show_bin=True, show_dec=True, show_hex=True):
        '''
        Instantiate a Net, depending on what was passed in.
        '''
        self.orig   = net
        self.mask   = None
        self.masked = None
        self.raw    = None

        # Specify how this Net is to be displayed.
        self.formats = {}
        self.formats['quad'] = { 'as string': None, 'show': show_quad }
        self.formats['bin']  = { 'as string': None, 'show': show_bin }
        self.formats['dec']  = { 'as string': None, 'show': show_dec }
        self.formats['hex']  = { 'as string': None, 'show': show_hex }

        base_address = None
        netmask      = None

        # What was passed in - maybe a.b.c.d/m?
        if '/' in self.orig:
            # Max of one slash, mkay?
            if self.orig.count('/') > 1:
                raise ValueError('Invalid CIDR block (multiple "/"es): ' + self.orig)
            # Ok, looks good.
            else:
                base_address, netmask = self.orig.split('/')
                self.mask = Net(netmask, show_quad, show_bin, show_dec, show_hex)
        
        # Or maybe an int of some sort...
        elif '.' not in self.orig:
            # A decimal number?
            if (len(self.orig) <= 10
                    and re.search(r'\d', self.orig) != None
                    and re.search(r'\D', self.orig) == None):
                # Special case - if self.orig is <= 32, we assume it was a
                # mask in a cidr block (eg - /24) rather than a decimal value
                # to be translated into an ip.
                if int(self.orig) <= 32:
                    base_address = bits2int(self.orig)
                else:
                    base_address = self.orig
            # How about a hex string?
            elif (len(self.orig) <= 8
                    and re.search(r'(?i)[^0-9a-f]', self.orig) == None):
                base_address = '0x' + self.orig
            # Right.  No clue what we were given.  Bailing.
            else:
                raise ValueError('Invalid CIDR block (invalid numeric value): ' + self.orig)

        # Alright, none of those - how about just plain a.b.c.d?
        else:
            base_address = self.orig

        # Now to populate the various representations of the Net.  Not bothering
        # to check which format was requested - the translations just aren't that
        # expensive.
        #
        # NOTE: The reason for the struct.unpack call is to allow this to work in
        #       both python2.x and python3.x
        # NOTE: inet_aton() throws an OSError on bad input, which should be caught
        #       by the caller.
        self.raw                          = socket.inet_aton(base_address)
        self.formats['quad']['as string'] = '.'.join('{:>3}'.format(o)
                                                for o in socket.inet_ntoa(self.raw).split('.'))
        self.formats['dec']['as string']  = '{:010d}'.format(int(sum(256**(3-x)*struct.unpack('B', self.raw[x:x+1])[0]
                                                for x in range(4))))
        self.formats['hex']['as string']  = '{:08x}'.format(int(self.formats['dec']['as string']))
        self.formats['bin']['as string']  = ' '.join('{:08b}'.format(int(o))
                                                for o in self.formats['quad']['as string'].split('.'))
        if self.mask:
            self.masked     = self & self.mask

    def __and__(self, other):
        '''
        Overloading '&' to apply a netmask.  That's really what's going on
        anyway, and it just makes sense.
        '''
        newnet = bytearray(socket.inet_aton('0.0.0.0'))

        # NOTE: Using struct.unpack so this works in both python2.x and python 3.x
        for o in range(4):
            newnet[o] = struct.unpack('B', self.raw[o:o+1])[0] & struct.unpack('B', other.raw[o:o+1])[0]

        # Inheriting the display formats from self.
        return Net(socket.inet_ntoa(bytes(newnet)),
                *(self.formats[fmt]['show'] for fmt in self.all_formats))

    def __str__(self):
        '''
        Return the translation of the IP (or netblock) as its various alternate formats,
        based on what the user requested.
        '''
        the_string = '  '
        
        the_string = '  <=>  '.join(self.formats[fmt]['as string']
                                for fmt in self.all_formats
                                if self.formats[fmt]['show'])

        if self.mask:
            the_string  =   '   ' + the_string
            the_string += '\n & ' + str(self.mask)
        if self.masked:
            the_string += '\n = ' + str(self.masked)

        return the_string

def bits2int(mask):
    """
    Change, for example, 24 or '24' into '4294967040'.   It returns
    the stringified version of the integer, in other words.
    NOTE: Currently only v4; will need update for v6.
    """
    try:
        mask = int(mask)
    except:
        raise ValueError('Invalid netmask, non-numeric: ' + mask)
    else:
        if 1 <= mask <= 32:
            return str(int("1"*mask+"0"*(32-mask),2))
        else:
            raise ValueError('Invalid netmask, outside of 1 <= m <= 32 range: ' + str(mask))


if __name__ == "__main__":

    import argparse

    argparser = argparse.ArgumentParser(
                            description="Display v4 IPs and/or CIDR blocks in dotted-quad, binary, hex, and decimal.",
                            epilog='''You can specify any combination of the --quad, --binary, --decimal, and --hexadecimal
                            options together to get multiple formats.  The default is to show all of them.''')
    argparser.add_argument('addresses',
                            nargs='+',
                            help='List of IPs or CIDR blocks to process.')
    argparser.add_argument('--mask',
                            action='append',
                            help='The mask to apply the addresses.')
    argparser.add_argument('--quad',
                            action='store_true',
                            help='Only display the addresses as dotted quads.')
    argparser.add_argument('--binary',
                            action='store_true',
                            help='Only display the addresses as binary.')
    argparser.add_argument('--decimal',
                            action='store_true',
                            help='Only display the addresses as base-10 ints.')
    argparser.add_argument('--hexadecimal',
                            action='store_true',
                            help='Only display the addresses as hexadecimal ints.')
    args = argparser.parse_args()

    formats = []
    if args.quad or args.binary or args.decimal or args.hexadecimal:
        formats = [ args.quad, args.binary, args.decimal, args.hexadecimal ]

    for cidr in args.addresses:
        # Making this a list in case the user specifies multiple --mask's
        cidrs = []

        # If the user specifies --mask m and a bare address,
        # change the constructor arg to 'a.b.c.c/m'.
        if '/' not in cidr and args.mask:
            for mask in args.mask:
                cidrs.append(cidr + '/' + mask)
        # Otherwise, just pass on what we got.
        else:
            cidrs.append(cidr)

        for net in cidrs:
            print(net + " :")
            print('=' * len(net))

            try:
                this_net = Net(net, *formats)
            except (ValueError, OSError, socket.error) as e:
                print('Error: ' + str(e))
                print('Skipping')
                print('')
                continue

            print(this_net)
            print('')
