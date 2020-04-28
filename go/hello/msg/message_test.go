package msg

import "testing"

func TestHelloMessage(t *testing.T) {
    want := "Hello!"
    if got := HelloMessage(); got != want {
        t.Errorf("Echo() = %q, want %q", got, want)
    }
}