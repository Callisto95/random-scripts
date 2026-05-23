import javax.crypto.Cipher;
import javax.crypto.CipherInputStream;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.charset.Charset;

public class DecryptFile {

    public static boolean decryptFile(String inputFile, String outputFile) {
        try {
            // Equivalent to C# UnicodeEncoding (UTF-16LE)
            String keyString = "h3y_gUyZ";
            byte[] keyBytes = keyString.getBytes(Charset.forName("UTF-16LE"));

            SecretKeySpec keySpec = new SecretKeySpec(keyBytes, "AES");
            IvParameterSpec ivSpec = new IvParameterSpec(keyBytes);

            // AES/CBC/PKCS5Padding in Java = PKCS7 compatible
            Cipher cipher = Cipher.getInstance("AES/CBC/PKCS5Padding");
            cipher.init(Cipher.DECRYPT_MODE, keySpec, ivSpec);

            FileInputStream fis = new FileInputStream(inputFile);
            CipherInputStream cis = new CipherInputStream(fis, cipher);
            FileOutputStream fos = new FileOutputStream(outputFile);

            int b;
            while ((b = cis.read()) != -1) {
                fos.write(b);
            }

            fos.close();
            cis.close();
            fis.close();

            return false; // success (matches C# behavior)

        } catch (Exception e) {
            new File(outputFile).delete();
            return true; // failure (matches C# behavior)
        }
    }

    public static void main(String[] args) {
        if (args.length != 2) {
            System.out.println("Usage: java DecryptFile inputFile outputFile");
            return;
        }

        boolean failed = decryptFile(args[0], args[1]);
        if (failed) {
            System.out.println("Decryption failed.");
        } else {
            System.out.println("Decryption successful.");
        }
    }
}
