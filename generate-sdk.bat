del /F /S /Q api-src
java -jar tools\swagger-codegen-cli-2.4.9.jar generate ^
	-i http://localhost:7080/swagger.json ^
	-c sdk-config.json ^
	-l python ^
	-o api-src
