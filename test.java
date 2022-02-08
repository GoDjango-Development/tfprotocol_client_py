
import javax.crypto.Cipher;

import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.charset.StandardCharsets;
import java.security.KeyFactory;
import java.security.PublicKey;
import java.security.spec.X509EncodedKeySpec;
import java.time.Instant;
import java.util.Arrays;
import java.util.Base64;

class TestCryptography {
    public static byte[] getRandomBytes(int length) {
        byte[] result = new byte[length];
        byte distanceFactor = 1;
        for (int i = 0; i < length; i++) {
            result[i] = (byte) (((Instant.now().getNano() * distanceFactor) % 126) + 1);
            distanceFactor += (i + 1) * result[i];
        }
        return result;
    }

    public static class RSA {
        public static byte[] encrypt(byte[] payload, String publicKey) {
            try {
                KeyFactory keyFactory = KeyFactory.getInstance("RSA");
                byte[] parsedPublicKey = publicKey.replace("-----BEGIN PUBLIC KEY-----", "")
                        .replaceAll("\r\n", "")
                        .replaceAll("\n", "")
                        .replace("-----END PUBLIC KEY-----", "")
                        .getBytes(StandardCharsets.UTF_8);

                // X509EncodedKeySpec keySpec = new
                // X509EncodedKeySpec(Base64.getDecoder().decode(parsedPublicKey));
                X509EncodedKeySpec keySpec = new X509EncodedKeySpec(Base64.getDecoder().decode(parsedPublicKey));
                PublicKey publicKeyObject = keyFactory.generatePublic(keySpec);
                Cipher cipher = Cipher.getInstance("RSA/ECB/OAEPWithSHA-1AndMGF1Padding");
                cipher.init(Cipher.ENCRYPT_MODE, publicKeyObject);
                return cipher.doFinal(payload, 0, payload.length);
            } catch (Exception e) {
                System.out.println("An error has occurredKey. " + e.toString() + '0');
                return "".getBytes();
            }
        }
    }

    public static class Xor {
        private static byte[] sessionKey;
        private byte[] key;
        private long seed;

        public Xor(byte[] key) {
            TestCryptography.Xor.sessionKey = key.clone();
            this.key = key.clone();
            this.seed = this.getNewSeed();
        }

        private long getNewSeed() {
            /*
             * return key[0] | key[1] << 8 | key[2] << 16 | key[3] << 24 |
             * (long)key[4] << 32 | (long)key[5] << 40 | (long)key[6] << 48 |
             * (long) key[7] << 56;
             */
            return ByteBuffer.wrap(Arrays.copyOfRange(this.key, 0, Long.BYTES))
                    .order(ByteOrder.LITTLE_ENDIAN).getLong();
        }

        public static byte[] getStaticSessionKey() {
            return sessionKey;
        }

        public byte[] encrypt(byte[] payload) {
            for (int c = 0; c < payload.length; c++) {
                payload[c] ^= this.key[c % this.key.length];
                /* Pack data to send */
                payload[c] += (byte) (this.seed >> 56 & 0xFF);
                /* Change seed and encryption key */

                this.seed = this.seed * (this.seed >> 8 & 0xFFFFFFFFL) +
                        (this.seed >> 40 & 0xFFFF);
                if (this.seed == 0) {
                    this.seed = getNewSeed();
                }
                this.key[c % this.key.length] = (byte) (this.seed % 256);
            }
            return payload;
        }

        public byte[] decrypt(byte[] payload) {
            for (int c = 0; c < payload.length; c++) {
                /* Unpack received data */
                payload[c] -= (byte) (this.seed >> 56 & 0xFF);
                /* Decrypt received data */
                payload[c] ^= this.key[c % this.key.length];
                this.seed = this.seed * (this.seed >> 8 & 0xFFFFFFFFL) +
                        (this.seed >> 40 & 0xFFFF);
                if (this.seed == 0) {
                    this.seed = getNewSeed();
                }
                this.key[c % this.key.length] = (byte) (this.seed % 256);
            }
            return payload;
        }

        public long getSeed() {
            return this.seed;
        }
    }

    public static class AES {
    }

    private static String readFromInputStream(InputStream inputStream)
            throws IOException {
        StringBuilder resultStringBuilder = new StringBuilder();
        try (BufferedReader br = new BufferedReader(new InputStreamReader(inputStream))) {
            String line;
            while ((line = br.readLine()) != null) {
                resultStringBuilder.append(line).append("\n");
            }
        }
        return resultStringBuilder.toString();
    }

    public static String hexlify(byte[] bytes) {
        char[] hexArray = "0123456789ABCDEF".toCharArray();
        char[] hexChars = new char[bytes.length * 2];
        for (int j = 0; j < bytes.length; j++) {
            int v = bytes[j] & 0xFF;
            hexChars[j * 2] = hexArray[v >>> 4];
            hexChars[j * 2 + 1] = hexArray[v & 0x0F];
        }
        String ret = new String(hexChars);
        return ret;
    }

    public static byte[] unhexlify(String argbuf) {
        int arglen = argbuf.length();
        if (arglen % 2 != 0)
            throw new RuntimeException("Odd-length string");

        byte[] retbuf = new byte[arglen / 2];

        for (int i = 0; i < arglen; i += 2) {
            int top = Character.digit(argbuf.charAt(i), 16);
            int bot = Character.digit(argbuf.charAt(i + 1), 16);
            if (top == -1 || bot == -1)
                throw new RuntimeException("Non-hexadecimal digit found");
            retbuf[i / 2] = (byte) ((top << 4) + bot);
        }
        return retbuf;
    }

    public static void main(String[] args) {
        ByteBuffer data = StandardCharsets.UTF_8.encode("I met aliens in UFO. Here is the map.");

        try {
            FileInputStream inputStream = new FileInputStream("public.key");
            String publicKey = readFromInputStream(inputStream);

            // var randombyts = getRandomBytes(16);
            var randombyts = unhexlify("030929B9D3BF9B09BD654D59DD432961");
            System.out.println("Session Key: " + hexlify(randombyts));
            var result = RSA.encrypt(randombyts, publicKey);
            System.out.println("Session Key Crypted: " + hexlify(result));

            // encrypt data
            Xor.sessionKey = result.clone();
            var xor = new Xor(result);
            System.out.println("\nMessage: " + xor.seed);
            System.out.println("\nMessage: " + hexlify(xor.encrypt(data.array())));

            var i = ByteBuffer.wrap(Arrays.copyOfRange(randombyts, 0, Long.BYTES))
                    .order(ByteOrder.LITTLE_ENDIAN).getLong();

            System.out.println(i);

        } catch (Exception e) {
            // if any exception is thrown the verification has failed
            e.printStackTrace();
            System.out.println("Verification Failed!");
        }
    }

}
