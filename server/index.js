var app = require('express')();
var http = require('http').Server(app);
var io = require('socket.io')(http);
var mysql      = require('mysql');
var connection = mysql.createConnection({
  host     : 'localhost',
  user     : 'root',
  password : '123456',
  database : 'software_engineering'
});
connection.connect();
function sleep(milliSeconds){
    var StartTime =new Date().getTime();
    let i = 0;
    while (new Date().getTime() <StartTime+milliSeconds);
}
app.get('/', function(req, res){
        res.send('<h1>Welcome Realtime Server</h1>');
});

//在线用户
var onlineUsers = {};
//当前在线人数
var onlineCount = 0;

io.on('connection', function(socket){

        //监听新用户加入
        socket.on('login', function(obj){
                //将新加入用户的唯一标识当作socket的名称，后面退出的时候会用到
                socket.name = obj.userid;
                connection.query('SELECT id from talk_robot where id=?',[obj.username], function (error, results, fields) {
                  if (error) throw error;
                  if (results[0]==null){
                        connection.query('insert into talk_robot(id,c_to_s,s_to_c,model)values(?,?,?,?)',[obj.username,"","",1],function (error, results, fields) {
                          if (error) throw error;
                        });
                  }
                });
                //检查在线列表，如果不在里面就加入
                if(!onlineUsers.hasOwnProperty(obj.userid)) {
                        onlineUsers[obj.userid] = obj.username;
                        //在线人数+1
                        onlineCount++;

                        //向所有客户端广播用户退出
                        io.emit('login', {onlineUsers:onlineUsers, onlineCount:onlineCount, user:obj});
                }
        });
        //监听用户退出
        socket.on('disconnect', function(){
                //将退出的用户从在线列表中删除
                if(onlineUsers.hasOwnProperty(socket.name)) {
                        //退出用户的信息
                        var obj = {userid:socket.name, username:onlineUsers[socket.name]};

                        //删除
                        delete onlineUsers[socket.name];
                        //在线人数-1
                        onlineCount--;

                        //向所有客户端广播用户退出
                        io.emit('logout', {onlineUsers:onlineUsers, onlineCount:onlineCount, user:obj});
                }
        });

        //监听用户发布聊天内容
        socket.on('message', function(obj){
                var s_to_c="";
                connection.query('SELECT s_to_c from talk_robot where id=?',[obj.username], function (error, results, fields) {
                  if (error) throw error;
                  s_to_c=results[0].s_to_c;
                  io.emit('message', obj);
	                console.log(s_to_c);
	                console.log(0);
                	connection.query('update talk_robot set c_to_s=? where id=?',[obj.content,obj.username], function (error, results, fields) {
	                  if (error) throw error;
	                  console.log('00');
	                  var i=10;
                		var j=0;
                		var k=0;
                		while(i>0){
                				i--;
                				console.log(i+10);
                        connection.query('SELECT s_to_c from talk_robot where id=?',[obj.username], function (error, results, fields) {
                        	console.log(i);
                        	if (error) throw error;
                        	console.log(results[0].s_to_c);
	                        sleep(1000);
	                        if(s_to_c!=results[0].s_to_c&&s_to_c!="对不起，没能理解您的意思。"){
	                                s_to_c=results[0].s_to_c;
	                                console.log(s_to_c);
	                                j=1;
	                        }
	                        i++;
	                        if(i==9){
				                    s_to_c="对不起，没能理解您的意思。";
				                    j=1;
													}
													if (j==1&&k==0) {
														obj.userid=0;
						                obj.content=s_to_c;
						                io.emit('message', obj);
						                k=1;
						                return false;
													}
                        });
                		}

	                });
                });
                //向所有客户端广播发布的消息
                
        });

});

http.listen(8888, function(){
        console.log('listening on *:8888');
});
