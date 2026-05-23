def main [] {
    try {
        sudo modprobe -r usbhid;
    }
    try { 
        sudo modprobe -r psmouse;
    }
    try {
        sudo modprobe usbhid;
    }
    try {
        sudo modprobe psmouse;
    }
}
