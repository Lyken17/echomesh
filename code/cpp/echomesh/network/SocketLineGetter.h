#ifndef __ECHOMESH_SOCKET_LINE_GETTER__
#define __ECHOMESH_SOCKET_LINE_GETTER__

#include "echomesh/network/LineGetter.h"

namespace echomesh {

class LineQueue;

struct SocketDescription {
  String server;
  int port;
  int timeout;
  int bufferSize;
  int tries;
  int retryTimeout;
  bool debug;
};

class SocketLineGetter : public LineGetter {
 public:
  SocketLineGetter(const SocketDescription&);
  virtual ~SocketLineGetter();

  static SocketLineGetter* instance();

  virtual string getLine();
  virtual bool eof() const { return eof_; }

  void writeSocket(const char*, int);
  virtual bool debug() const { return desc_.debug; }
  virtual void requestQuit() {
    ScopedLock l(lock_);
    quitRequested_ = true;
  }

 private:
  string readSocket();
  void check(bool, const String&);

  void tryToConnect();

  StreamingSocket socket_;
  vector<char> buffer_;
  const SocketDescription desc_;
  bool connected_;
  bool eof_;
  bool quitRequested_;
  CriticalSection lock_;

  ScopedPointer<LineQueue> lineQueue_;

  DISALLOW_COPY_AND_ASSIGN(SocketLineGetter);
};

}  // namespace echomesh

#endif  // __ECHOMESH_SOCKET_LINE_GETTER__
