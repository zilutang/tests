package top.usking.sky.knowledge.nebula;

import com.vesoft.nebula.client.graph.SessionPool;
import com.vesoft.nebula.client.graph.data.ResultSet;
import com.vesoft.nebula.client.graph.exception.AuthFailedException;
import com.vesoft.nebula.client.graph.exception.BindSpaceFailedException;
import com.vesoft.nebula.client.graph.exception.ClientServerIncompatibleException;
import com.vesoft.nebula.client.graph.exception.IOErrorException;
import lombok.extern.slf4j.Slf4j;
import top.usking.sky.knowledge.common.ResultCode;
import top.usking.sky.knowledge.exception.NebulaClientException;
import top.usking.sky.knowledge.nebula.ddl.operations.EdgeTypeTemplate;
import top.usking.sky.knowledge.nebula.ddl.operations.TagTemplate;
import top.usking.sky.knowledge.nebula.enums.DataModelEnum;
import top.usking.sky.knowledge.nebula.model.Clause;

import javax.annotation.Resource;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

/**
 * 操作图数据空间内的对象的抽象类。
 * <p>
 * 此抽象类主要是对空间内对象的操作。<br>
 * <pre>
 * 例如：
 * TAG,EDGE TYPE,VERTEX,EDGE,INDEX
 * </pre>
 * </p>
 *
 * @author sky
 * @see TagTemplate
 * @see EdgeTypeTemplate
 * @see top.usking.sky.knowledge.nebula.dml.operations.EdgeTemplate
 * @see top.usking.sky.knowledge.nebula.dml.operations.VertexTemplate
 * @since 2023-11-08
 */
@Slf4j
public abstract class AbsSpaceOperations extends AbsBaseOperations {

    protected static final String COUNT_CLAUSE = "| YIELD COUNT(*) AS cnt";
    protected static final String LOOKUP_COMMAND = "LOOKUP ON %s %s YIELD %s AS x %s";

    @Resource
    private SpaceSessionFactory factory;

    /**
     * 调用Nebula的执行方法。
     *
     * @param command   命令。
     * @param spaceName 图空间。
     * @return 返回 {@link ResultSet}结果。
     */
    @Override
    public ResultSet execute(String command, String spaceName) {
        SessionPool session = null;
        // 设置重试次数
        int retryCount = 5;
        // 每次重试之间的等待时间（毫秒）
        int waitTime = 2000;
        for (int attempt = 0; attempt < retryCount; attempt++) {
            if (attempt > 0) {
                log.warn("Nebula连接失败, 第{}次尝试连接图数据库", attempt + 1);
            }
            try {
                session = factory.openSession(spaceName);
                if (session != null) {
                    break;
                }
            } catch (NebulaClientException e) {
                try {
                    Thread.sleep(waitTime);
                } catch (InterruptedException ex) {
                    throw new RuntimeException(ex);
                }
            }
        }
        if (session == null) {
            throw new NebulaClientException(ResultCode.CONNECT_SPACE_ERROR, "图数据库连接失败达最大重试次数");
        }
        log.info("nGQL:[{}]", command);
        ResultSet resp;
        try {
            resp = session.execute(command);
        } catch (IOErrorException
                 | ClientServerIncompatibleException
                 | AuthFailedException
                 | BindSpaceFailedException e) {
            log.error("Execute nGQL occur error. message:[{}]", e.getMessage());
            throw new RuntimeException(e);
        }
        if (!resp.isSucceeded()) {
            log.error("Execute: `{}', failed: {}", command, resp.getErrorMessage());
            throw new RuntimeException("nebula语句执行失败:" + command + "failed:" + resp.getErrorMessage());
        }
        return resp;
    }

    public Long count(String name, DataModelEnum modelEnum, String whereClause, String spaceName) {
        if (modelEnum == DataModelEnum.TAG) {
            modelEnum = DataModelEnum.VERTEX;
        }
        String nGql = buildNGql(LOOKUP_COMMAND, name, new Clause(whereClause), modelEnum, COUNT_CLAUSE);
        ResultSet resultSet = execute(nGql, spaceName);
        if (resultSet.isSucceeded()) {
            return resultSet.getRows().get(0).getValues().get(0).getIVal();
        }
        return 0L;
    }

    protected static <T> void checkPairList(List<T> a, List<T> b) {
        if (a.size() != b.size()) {
            throw new IllegalArgumentException("列表对长度不匹配");
        }
    }

    protected static String buildInsertPropParam(List<String> propNames, List<String> propValues) {
        checkPairList(propNames, propValues);
        return propValues.stream()
                .map(value -> {
                    if (value == null) {
                        return "null"; // 处理 null 值
                    }
                    // 转义双引号
                    value = escapeCharacters(value);
                    return String.format("\"%s\"", value); // 使用双引号包裹字符串
                })
                .collect(Collectors.joining(", ", "(", ")"));
    }

    protected static String buildUpdatePropParam(List<String> propNames, List<String> propValues) {
        checkPairList(propNames, propValues);
        return IntStream.range(0, propNames.size())
                .mapToObj(i -> {
                    String propName = escapeCharacters(propNames.get(i));
                    String propValue = escapeCharacters(propValues.get(i));
                    return String.format("%s=\"%s\"", propName, propValue);
                })
                .collect(Collectors.joining(", "));
    }
}
