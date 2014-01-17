'''
Questo coso rioridina i log di weechat facendo in modo che le frasi di un nick
non siano intramezzate con quelle di altre persone

Nel farlo, elimina le righe che non sono messaggi
'''
import sys
from datetime import datetime
import logging
logging.basicConfig(level=logging.DEBUG)


class Message(object):
    def __init__(self, nick, text, date=None):
        self.nick = nick
        self.text = text
        self.date = date  # TODO: or datetime(1970)

    def __getitem__(self, key):
        return getattr(self, key)


def pre_filter(buf):
    '''
    Read logs and yields Messages; it just does parsing + filters away
    join/part/action messages
    '''
    for line in buf:
        line = line.replace('\0', '').strip()
        if line.count('\t') < 2:
            continue
        try:
            date, nick, text = line.split('\t', 2)
            date = datetime.strptime(date.strip(), '%Y-%m-%d %H:%M:%S')
        except Exception:
            logging.exception("Error on line '%s'" % line)
            for char in line:
                print '\t%d' % ord(char)
            sys.exit(1)
        else:
            if nick.startswith('<--') or nick[0] in '- ' \
               or nick.startswith('***'):
                continue
            if text.startswith('['):  # bouncer replays, a bit too aggressive
                continue
            yield Message(nick, text, date)


def intelligent_sort(messages):
    '''
    iterable is a sequence of Message instances.
    We want to sort by nick in a stable way
    '''
    l = list(messages)
    l.sort(key=lambda x: x.nick)
    return l

### TODO: raggruppa frasi molto vicine nel tempo

if __name__ == '__main__':
    # TODO: opzioni per (non) mostrare nick
    # TODO: opzioni per selezionare per nick
    # TODO: opzioni per specificare formato

    path = sys.argv[1]
    for msg in intelligent_sort(pre_filter(open(path))):
        #print '%s\t%s' % (msg.nick, msg.text)
        #print '%s\t%s\n' % (msg.nick, msg.text)
        print '%(text)s\n' % msg
