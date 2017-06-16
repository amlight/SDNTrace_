from libs.core.singleton import Singleton
from libs.topology.link import Link


class Links:
    """
    
    """

    __metaclass__ = Singleton

    def __init__(self):
        self.links = []
        self.temp_links = []

    def process_new_link(self, new_link):
        """

            Args:
                new_link: 
    
            Returns:

        """
        if not self._check_if_exist(new_link, self.links):
            if self._check_if_bidirectional(new_link):
                self._add_link(new_link)
                return True
        return False

    def _check_if_bidirectional(self, link):
        """
            To be added, Links need to see both directions. Every link received
            is first added to self.temp_links.  Once an inverse direction link
            is detected, return True to add link.
            Args:
                link: 

            Returns:

        """
        # if link already is part of self.links, ignore
        if self._check_if_exist(link, self.links):
            return False

        # if link already is part of self.temp_links, ignore
        if self._check_if_exist(link, self.temp_links):
            # ignore
            return False

        # if link does not exist but its inverse direction does,
        # add to self.links
        switch_a = link.switch_a
        port_a = link.port_a
        switch_z = link.switch_z
        port_z = link.port_z
        inverse = Link(switch_z, port_z, switch_a, port_a)

        if self._check_if_exist(inverse, self.temp_links):
            self.temp_links.remove(inverse)
            del inverse
            return True

        del inverse

        # If link or its inverse direction do not exist, add it
        # to self.temp_links
        self.temp_links.append(link)

    def _check_if_exist(self, new_link, links):
        """
        
            Args:
                new_link: 
    
            Returns:

        """
        for link in links:
            if new_link == link:
                return True
        return False

    def _add_link(self, new_link):
        """
        
            Args:
                new_link: 
    
            Returns:

        """
        self.links.append(new_link)
        print("New Link Detected: %s:%s - %s:%s" %
              (new_link.switch_a, new_link.port_a,
               new_link.switch_z, new_link.port_z))

    @property
    def simple(self):
        """
        
            Returns:

        """
        new_list = []
        for link in self.links:
            new_link = link.switch_a, link.switch_z
            new_list.append(new_link)
        return new_list

    def remove_switch(self, switch):
        """
        
            Args:
                switch: 
    
            Returns:

        """
        for link in self.links:
            if link.switch_a == switch or link.switch_z == switch:
                self.links.remove(link)
                del link

    def __str__(self):
        """
        
            Returns:

        """
        string = ""
        for link in self.links:
            if link is not None:
                string += str(link)
        return string

    def __len__(self):
        """
        
            Returns:

        """
        return len(self.links)
