import os
import io
import hashlib
import base64
import pycurl

from PyQt5.QtCore import QByteArray

import qiniu


class FileStore:
    def __init__(self):
        return

    def uploadData(data):
        return

    def uploadFile(fname):
        return

    def md5sum(data):
        h = hashlib.md5()
        h.update(data)
        return h.hexdigest()


class QiniuFileStore(FileStore):
    def __init__(self):
        return

    # @param data bytes | QByteArray
    def uploadData(data):
        if type(data) == QByteArray:
            data = data.data()

        from .secfg import qiniu_acckey, qiniu_seckey, qiniu_bucket_name
        access_key = qiniu_acckey
        secret_key = qiniu_seckey
        bucket_name = qiniu_bucket_name

        q = qiniu.Auth(access_key, secret_key)
        key = 'helloqt.png'
        key = FileStore.md5sum(data)
        # data = 'hello qiniu!'
        # data = load_from_file(PATH)
        token = q.upload_token(bucket_name)
        ret, info = qiniu.put_data(token, key, data)
        if ret is not None:
            print('upload file All is OK', ret)
        else:
            print(ret, '=====', info)  # error message in info

        url = 'http://7xn2rb.com1.z0.glb.clouddn.com/%s' % key
        return url

    def uploadFile(fname):
        data = b''
        with open(fname, 'rb') as f:
            data = f.read()

        return QiniuFileStore.uploadData(data)


class ImgurFileStore(FileStore):
    def __init__(self):
        return

    def uploadData(data):
        return

    def uploadFile(fname):
        return


class VnFileStore(FileStore):
    def __init__(self):
        return

    def uploadData(data):
        return 'nourl'
        if type(data) == QByteArray:
            data = data.data()

        md5sum = FileStore.md5sum(data)
        fname = '/tmp/' + md5sum

        with open(fname, 'wb') as f:
            f.write(data)

        url = VnFileStore.uploadFile(fname)
        os.path.os.unlink(fname)
        return url

    def uploadFile(fname):
        dest_url = b'aHR0cHM6Ly9pbWcudmltLWNuLmNvbS8='  # heihei
        dest_url = base64.b64decode(dest_url).decode()

        c = pycurl.Curl()
        c.setopt(pycurl.URL, dest_url)
        c.setopt(pycurl.POST, 1)

        filename = fname
        c.setopt(c.HTTPPOST, [(('file', (c.FORM_FILE, filename)))])
        c.setopt(pycurl.SSL_VERIFYPEER, 0)
        c.setopt(pycurl.SSL_VERIFYHOST, 0)
        c.setopt(pycurl.USERAGENT, 'curl/7.45.0')
        # c.setopt(pycurl.VERBOSE, 1)
        # c.setopt(pycurl.PROXY, '127.0.0.1:8117')
        # c.setopt(pycurl.PROXYTYPE_HTTP, 1)

        outval = io.BytesIO()
        hdrval = io.BytesIO()
        c.setopt(pycurl.WRITEFUNCTION, outval.write)
        c.setopt(pycurl.HEADERFUNCTION, hdrval.write)
        c.setopt(pycurl.TIMEOUT, 107)  # 这网烂成如此，不容易

        c.perform()
        c.close()

        # print(outval.getvalue().decode(), hdrval.getvalue().decode())
        url = outval.getvalue().decode()
        if not url.startswith('https://'): print('upload error: ', hdrval.getvalue())

        return url
