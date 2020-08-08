from contro import Controller


def main():
    Con = Controller()
    m = Con.master
    s1 = m.createSlave()
    s = m.getSlave('Cust1', s1.id)
    m.on()
    s.on()
    t = Con.checkThread()


if __name__ == '__main__':
    main()
