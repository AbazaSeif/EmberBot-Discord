import sys

def coin_float_to_bignum(x: float):
        x_str = "{:.8f}".format(x)
        x_str_new = x_str[:-9]+x_str[-8:]
        print("float to bignum: ")
        print(x)
        print(x_str)
        print(x_str_new)
        if sys.version_info > (3,):
            ret = int(x_str_new)
        else:
            ret = long(x_str_new)
        print(ret)
        return ret

def coin_bignum_to_float(x: int):
        x_str = str(x)
        if len(x_str) < 9:
            x_new = '0.{:08d}'.format(x)
        else:
            x_new = x_str[:-8]+'.'+x_str[-8:]
        ret = float(x_new)
        print("bignum to float: ")
        print(x)
        print(x_str)
        print(x_new)
        print(ret)
        return ret