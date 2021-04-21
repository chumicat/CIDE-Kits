import ipaddress as ip


class CIDRKits:
    @staticmethod
    def get_network_cast(net: ip.IPv4Address):
        return \
            'Unicast' if ip.IPv4Address('1.1.1.1') <= net <= ip.IPv4Address('223.255.255.255') else \
            'Multicast' if ip.IPv4Address('224.0.0.0') <= net <= ip.IPv4Address('239.255.255.255') else \
            'Limited Broadcast (local broadcast)' if net == ip.IPv4Address('255.255.255.255') else "Undefined"

    @staticmethod
    def get_network_class(net: ip.IPv4Network):
        return \
            'A' if ip.ip_network('0.0.0.0/1').supernet_of(net) else \
            'B' if ip.ip_network('128.0.0.0/2').supernet_of(net) else \
            'C' if ip.ip_network('192.0.0.0/3').supernet_of(net) else \
            'D' if ip.ip_network('224.0.0.0/4').supernet_of(net) else 'E'

    @staticmethod
    def get_network_info(net: str):
        network = ip.ip_interface(net).network
        netmask = ip.ip_interface(net).netmask
        netaddr = network.network_address
        brd_cst = ip.ip_network(network).broadcast_address
        host_cnt = ip.ip_network(network).num_addresses - 2

        return 'Netmask: {}\nNetwork: {}\n1stHost: {}\nLstHost: {}\nBrd Cst: {}\nHostCnt: {}' \
               '\nIPClass: Class {}\nCst Typ: {}' \
            .format(netmask, network,
                    (netaddr + 1 if host_cnt > 0 else '-'),
                    (brd_cst - 1 if host_cnt > 0 else '-'),
                    (brd_cst if host_cnt >= 0 else '-'),
                    (host_cnt if host_cnt > 0 else 0),
                    CIDRKits.get_network_class(network)
                    + (', Private' if network.is_private else ', Public')
                    + (' (Lookback)' if network.is_loopback else ''),
                    CIDRKits.get_network_cast(netaddr),
                    )

    @staticmethod
    def div_network_with_mask(net: str, mask_prefixlen: int):
        network = ip.ip_interface(net).network
        net_prefixlen = ip.ip_network(network).prefixlen
        brd_cst = ip.ip_network(network).broadcast_address

        output = ''
        if net_prefixlen <= int(mask_prefixlen) <= 32:
            net_bits = int(mask_prefixlen) - net_prefixlen
            host_bits = 32 - int(mask_prefixlen)

            # Basic Info
            output = 'Mask of Subnet: {}\nNet Cnt Total: {}\nHostCnt / Net: {}\nSubnets are as below:\n' \
                .format(ip.ip_address(4294967295 >> host_bits << host_bits), 2 ** net_bits, 2 ** host_bits - 2 if host_bits else 0)
            output += "       Idx.     Network       , Boardcast\n"

            # Subnets Info (No. 0-15 + last one)
            net2brd_dis = 2 ** host_bits - 1
            it = network.subnets(prefixlen_diff=net_bits)
            for idx, row in zip(range(16), it):
                output += '{:>10d}. {:<18s}, {:<15s}\n'.format(
                    idx, str(row), str(row.network_address + net2brd_dis) if host_bits else '-'
                )
            if net_bits > 4:
                output += '                  ...\n{:>10d}. {:<18s}, {}\n'.format(
                    2 ** net_bits - 1, str(brd_cst - 2 ** host_bits + 1), str(brd_cst) if host_bits else '-'
                )

        return output

    def update(self, *args):
        try:
            if self.var['prefixlen'].get() == '':
                output = CIDRKits.get_network_info(self.var['network'].get())
            else:
                output = CIDRKits.div_network_with_mask(self.var['network'].get(), self.var['prefixlen'].get())
        except ValueError:
            output = ''
        self.var['output'].set(output)

    def __init__(self):
        # Import only when Construct to prevent error while no tk host try to use staticmethod
        import tkinter as tk
        import tkinter.font as tkfont

        # TK Setting
        root = tk.Tk()
        root.title('CIDR Kits')
        root.geometry('600x300')
        root.wm_minsize(800, 800)
        root.wm_maxsize(800, 800)
        root.configure(background='white')
        font = tkfont.Font(size=20, family='Consolas')

        # TK mainframe structure
        (input_frame := tk.Frame(root)).pack(side=tk.TOP)
        (output_frame := tk.Frame(root)).pack(side=tk.TOP)

        # TK sub frame structure and variable dictionary
        # all variables will be bind to var
        # 'network' and 'prefixlen' are variables from user
        # 'output' is the output variables we have to write in
        self.var = {'network': tk.StringVar(value=''),
                    'prefixlen': tk.StringVar(value=''),
                    'output': tk.StringVar(value='')
                    }
        self.var['network'].trace('w', self.update)
        self.var['prefixlen'].trace('w', self.update)
        tk.Label(input_frame, font=font, text='Network').grid(row=0, column=0)
        tk.Entry(input_frame, font=font, textvariable=self.var['network'], width=18).grid(row=0, column=1)
        tk.Label(input_frame, font=font, text='Div with Prefix Length /').grid(row=0, column=2)
        tk.Entry(input_frame, font=font, textvariable=self.var['prefixlen'], width=3).grid(row=0, column=3)
        tk.Label(output_frame, font=font, textvariable=self.var['output'], width=53, anchor="w", justify=tk.LEFT)\
            .pack(side=tk.TOP)

        root.mainloop()


if __name__ == '__main__':
    CIDRKits()