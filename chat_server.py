import socket
import select

# Khởi tạo socket server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('localhost', 8080))
server_socket.listen()

# Khởi tạo danh sách các client đang kết nối
client_sockets = []

# Khởi tạo danh sách các tên client tương ứng
client_names = {}

# Hàm xử lý khi có kết nối mới
def handle_new_connection():
    client_socket, client_address = server_socket.accept()
    client_sockets.append(client_socket)
    print(f'Accepted new connection from {client_address}')

# Hàm xử lý khi có dữ liệu mới từ một client
def handle_client_data(client_socket):
    try:
        data = client_socket.recv(1024).decode().strip()
        if client_socket not in client_names:
            # Nếu client chưa đăng nhập tên thì yêu cầu đăng nhập
            if ':' not in data:
                client_socket.send('Please enter your name in the format "client_id: client_name"'.encode())
                return
            client_id, client_name = data.split(':')
            client_names[client_socket] = client_name.strip()
            print(f'{client_name} joined the chat')
            client_socket.send('You have successfully joined the chat'.encode())
        else:
            # Nếu client đã đăng nhập thì gửi tin nhắn đến các client khác
            sender_name = client_names[client_socket]
            message = f'{sender_name}: {data}'
            for other_socket in client_sockets:
                if other_socket != client_socket:
                    other_socket.send(message.encode())
    except:
        # Nếu có lỗi xảy ra thì xóa client khỏi danh sách
        client_sockets.remove(client_socket)
        client_name = client_names[client_socket]
        print(f'{client_name} left the chat')
        del client_names[client_socket]

# Chạy vòng lặp chính của server
while True:
    # Sử dụng select() để chờ kết nối hoặc dữ liệu mới
    read_sockets, _, _ = select.select([server_socket] + client_sockets, [], [])
    for sock in read_sockets:
        if sock == server_socket:
            handle_new_connection()
        else:
            handle_client_data(sock)
