with open('.spiceinit') as f,open('str','w') as ff:
    file=f.read()
    # print(file)
    ff.write(file.encode('unicode_escape').decode('ASCII'))
