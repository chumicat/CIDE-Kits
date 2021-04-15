import ipaddress as ip
import tkinter as tk
import tkinter.font as tkfont


class CIDRKits:
    def update(self, *args):
        try:
            network = ip.ip_interface(self.var['network'].get()).network
            netmask = ip.ip_interface(self.var['network'].get()).netmask
            prefixlen = ip.ip_network(network).prefixlen
            netaddr = network.network_address
            brd_cst = ip.ip_network(network).broadcast_address
            host_cnt = ip.ip_network(network).num_addresses - 2

            if self.var['prefixlen'].get() == '':
                output = 'Netmask: {}\nNetwork: {}\n1stHost: {}\nLstHost: {}\nBrd Cst: {}\nHostCnt: {}\n' \
                    .format(netmask, network,
                            (netaddr + 1 if host_cnt > 0 else '-'),
                            (brd_cst - 1 if host_cnt > 0 else '-'),
                            (brd_cst if host_cnt >= 0 else '-'),
                            (host_cnt if host_cnt > 0 else 0),
                            )
            elif prefixlen <= int(self.var['prefixlen'].get()) <= 32:
                net_bits = int(self.var['prefixlen'].get()) - prefixlen
                host_bits = 32 - int(self.var['prefixlen'].get())

                # Basic Info
                output = 'Net Cnt Total: {}\nHostCnt / Net: {}\nHosts are as below:\n'\
                    .format(2**net_bits, 2**host_bits - 2 if host_bits else 0)
                output += "Idx,    Network,     Boardcase\n"

                # Hosts Info (0-15 + lastone)
                net2brd_dis = 2**host_bits - 1
                it = network.subnets(prefixlen_diff=net_bits)
                for idx, row in zip(range(16), it):
                    output += "{}. {}, {}\n".format(idx, row, row.network_address + net2brd_dis if host_bits else '-')
                if net_bits > 4:
                    output += "...\n{}. {}\n".format(2 ** net_bits - 1, brd_cst - 2**host_bits + 1)
            else:
                output = ''
        except:
            output = ''

        # Write Output
        self.var['output'].set(output)

    def __init__(self):
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
        self.var = {'network': tk.StringVar(value=''), 'prefixlen': tk.StringVar(value=''), 'output': tk.StringVar(value='')}
        self.var['network'].trace('w', self.update)
        self.var['prefixlen'].trace('w', self.update)
        tk.Label(input_frame, font=font, text='Network').grid(row=0, column=0)
        tk.Entry(input_frame, font=font, textvariable=self.var['network'], width=18).grid(row=0, column=1)
        tk.Label(input_frame, font=font, text='Div with Prefix Length /').grid(row=0, column=2)
        tk.Entry(input_frame, font=font, textvariable=self.var['prefixlen'], width=3).grid(row=0, column=3)
        tk.Label(output_frame, font=font, textvariable=self.var['output'], width=53, anchor="w", justify=tk.LEFT)\
            .pack(side=tk.TOP)

        self.var['output'].set('no way')
        root.mainloop()


if __name__ == '__main__':
    CIDRKits()
